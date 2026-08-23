# B.E.A.M. AI — Training & Inference Infrastructure

Architecture, training framework and inference seam for B.E.A.M.
(Behavioral Emotion Analysis Model).

**Status:** infrastructure complete; **no transformer model is trained
yet** and no quality metrics exist, because no labeled dataset exists.
Everything below runs on CPU; CUDA is used automatically when present.

---

## Architecture

```
Dataset (beam-datasets/splits/dataset_<v>_{train,validation,test}.jsonl)
      |
TrainingConfig  (beam-ai/configs/*.yaml -> beam_ai.training.config)
      |
LabelConfig     (explicit labels OR dataset metadata label_schema)
      |                                   |
TokenizerPipeline               ModelFactory (BaseEmotionModel)
      |                                   |
      +----------- Trainer ----------------+
                  |  checkpoints/ per epoch
                  |  ExperimentTracker (JSONL runs)
                  v
          Model Artifact  beam-models/<model-name>/vNNN/
                  |
            Evaluation (scikit-learn metrics -> evaluation.json)
                  |
            Registry (beam-models/registry.json, status lifecycle)
                  |
   TransformerInferenceService -> TransformerAnalysisAdapter
                  |                     (future FastAPI hook)
        ExplanationPayload schema (SHAP/LIME prepared, NOT implemented)
```

Package layout:

```
beam_ai/
    configs/pipeline_settings.py    # dataset pipeline settings
    preprocessing/ features/ dataset_pipeline/   # existing data pipeline
    utils/         seeding.py device.py paths.py
    training/      config.py labels.py data.py tokenization.py
                   trainer.py tracker.py offline.py smoke_test.py __main__.py
    models/        base.py factory.py artifacts.py
    evaluation/    metrics.py evaluate.py
    registry/      registry.py
    inference/     service.py adapter.py explainability.py
beam-ai/
    configs/       train_distilbert.yaml  smoke_test.yaml
    scripts/       train.py
    tests/         dataset_pipeline/ (42)  training/ (78)
```

## Training workflow

```bash
# 0) verify plumbing in seconds (no network, untrained tiny model):
python -m beam_ai.training.smoke_test

# 1) train for real (requires a labeled dataset version!):
python -m beam_ai.training --config beam-ai/configs/train_distilbert.yaml

# 2) evaluate the artifact on the test split:
python -m beam_ai.evaluation.evaluate --artifact beam-models/<name>/v001

# 3) promote ONLY after real evaluation:
#    registry.update_status(name, version, "production")
```

`Trainer` does: load config -> load splits -> resolve labels ->
tokenizer -> model -> epoch loop (AdamW, linear warmup schedule, grad
clipping) -> validation metrics each epoch -> per-epoch checkpoint
(`beam-models/checkpoints/<run_id>/epoch_NN.pt`) -> best-epoch weights
saved as a full artifact -> run finalized in the JSONL experiment log.

## Configuration

All hyperparameters live in `TrainingConfig` (`beam_ai/training/config.py`)
and are loaded from YAML — never hardcoded in training code:
`model_name`, `model_type`, `dataset_version`, `learning_rate`,
`batch_size`, `epochs`, `max_sequence_length`, `random_seed`,
`warmup_ratio`, `weight_decay`, `output_directory`, plus `device`,
`class_weighting`, `sampling_strategy`, `text_column`, `label_column`,
optional explicit `labels` and `split_files` overrides.

Bundled configs:
- `configs/train_distilbert.yaml` — realistic DistilBERT run (blocked until a labeled dataset exists);
- `configs/smoke_test.yaml` — tiny random model, synthetic fixture, CPU-only.

## Dataset requirements

Splits come from the dataset engineering pipeline. For training, rows
need a text column (`cleaned_text`) and a label column (`label`). The
emotion label set is **not hardcoded**: provide it via `labels:` in YAML
or as `label_schema.labels` inside
`beam-datasets/metadata/dataset_<v>.json`. Unlabeled datasets (current
`v001`) are refused with an explicit error. Rows without labels are
counted and skipped, never silently mixed in.

## Class imbalance

Infrastructure is ready but OFF by default: `class_weighting: balanced`
(weighted CrossEntropyLoss) and `sampling_strategy: inverse_frequency`
(WeightedRandomSampler). Enable only when the class distribution of the
real labeled dataset justifies it.

## Model artifacts

```
beam-models/<model-name>/<version>/
    config.json           # HF architecture config (required to reload)
    training_config.json  # exact training configuration snapshot
    metadata.json         # task, dataset version, labels, REAL metrics or null, status
    tokenizer files / model weights (safetensors)
```

Version folders auto-increment (v001, v002, ...). `metrics` is `null`
until a genuine evaluation writes it — placeholders are forbidden.

## Evaluation

`beam_ai.evaluation.metrics.compute_classification_metrics` reports
accuracy, precision/recall/F1 (macro + weighted), confusion matrix,
per-class metrics and support (scikit-learn). `evaluate_artifact(...)`
runs a saved model over a split, writes `evaluation.json` next to the
artifact and marks the metadata `validated`. If no artifact exists you
get `ArtifactNotFoundError("No trained model artifact available ...")` —
never invented numbers.

## Model registry & experiment tracking

`beam-models/registry.json` (atomic JSON list): `model_name`,
`model_version`, `task`, `dataset_version`, `created_at`, `metrics`,
`artifact_path`, `status`. Lifecycle `training -> validated ->
production -> archived`; promotion to production is refused unless the
entry is validated **and** carries measured metrics. Production entries
also drop a pointer file into `beam-models/production/`.

Experiments append to `beam-models/experiments/runs.jsonl`: run id,
model/version/dataset versions, full config snapshot, seed, per-epoch
train loss + validation metrics, checkpoint paths, wall-clock duration,
timestamps. No secrets are recorded. Swap in MLflow later without
changing call sites.

## Inference

```python
from beam_ai.inference.service import TransformerInferenceService

service = TransformerInferenceService()          # resolves production entry
result = service.predict("I feel great today")   # PredictionResult
# primary_emotion, confidence, emotion_distribution,
# model_name, model_version, inference_time_ms (real measurement)

service.safe_predict(text)   # dict; "model_unavailable" state instead of raising
```

Without a registered/trained model the service reports an explicit
unavailable state — predictions are never fabricated.

### FastAPI preparation

`TransformerAnalysisAdapter.analyze(text)` returns a stable dict
(`engine`, emotion fields, `explanation_schema_version`, `explanation`)
that a future endpoint can merge into the analysis response while the
frontend contract stays untouched. With no model it returns
`status: model_unavailable` so the existing lexicon path keeps serving.

## Explainability (prepared, not implemented)

`ExplanationPayload` / `TokenAttribution` define where SHAP/LIME/token-
importance output will land (`important_tokens`, `feature_importance`,
`metadata`). `PlaceholderExplainer.explain()` raises
NotImplementedError by design. See `inference/explainability.py`.

## CPU / GPU usage

`resolve_device("auto"|"cpu"|"cuda")`: CUDA is used when available,
otherwise everything runs on CPU (the default development mode). Force
with `--device cpu|cuda`. Tiny/smoke models always stay on CPU.

## Reproducibility

Seeds are set for Python `random`, NumPy, PyTorch (+ all CUDA devices),
`PYTHONHASHSEED` is pinned and cuDNN autotuning disabled. Remaining
sources of nondeterminism: GPU kernels using atomic operations, cross-
hardware/library-version floating point drift, dropout trajectories
across framework upgrades. Same machine + same versions + same seed =>
identical data order and (CPU) bitwise-stable runs in practice.

## Testing

`pytest beam-ai/tests` → 120 tests (42 dataset pipeline + 78
infrastructure). Infrastructure tests cover configuration, label
mapping, dataset loading, tokenization determinism, model factory,
artifact save/load roundtrip, metrics vs hand-computed values, registry
lifecycle guards, inference unavailable-state and real-prediction shape,
explainability contract. All CPU-only, network-free (offline WordPiece
tokenizer + tiny random DistilBERT), and none require a trained model.

Smoke test (spec checklist):

```bash
python -m beam_ai.training.smoke_test
# [PASS] configuration loads / dataset loads / labels load /
#        tokenizer initializes / model factory initializes /
#        one batch forward+backward
```

It uses an UNTRAINED randomly-initialised tiny model and clearly
synthetic fixture data; it validates plumbing only and reports no
quality numbers.

## Future SHAP integration roadmap

1. implement `ExplainerProtocol` (e.g. SHAP partition explainer over the
   tokenizer output);
2. populate `TokenAttribution` from real attribution scores;
3. surface the payload through the adapter's `explanation` field;
4. add latency budget + tests with hand-computed attributions.

## Honesty rules enforced in code

- `metrics: null` until measured; evaluation refuses empty splits;
- inference raises/returns unavailable instead of guessing;
- smoke/demo runs are labelled as such wherever they print;
- the registry cannot mark anything production without real evaluation.
