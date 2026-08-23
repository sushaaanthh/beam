"""Training pipeline.

Responsibilities (per architecture spec):
load config -> load dataset -> load tokenizer -> load model -> train ->
validate each epoch -> save checkpoints -> save final artifact ->
log real metrics to the experiment tracker and registry.

The trainer never fabricates numbers: every logged metric is produced by
an actual evaluation pass over the validation split.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from beam_ai.evaluation.evaluate import collect_predictions
from beam_ai.models.artifacts import artifact_dir_for, next_model_version, save_artifact
from beam_ai.registry.registry import Registry
from beam_ai.training.config import TrainingConfig
from beam_ai.training.labels import LabelConfig
from beam_ai.utils.device import resolve_device
from beam_ai.utils.seeding import set_seeds


@dataclass
class TrainResult:
    run_id: str
    model_name: str
    model_version: str
    artifact_dir: Path | None
    best_epoch: int
    best_val_metrics: dict | None
    duration_seconds: float


class Trainer:
    def __init__(
        self,
        config: TrainingConfig,
        label_config: LabelConfig | None = None,
        tracker=None,
        registry: Registry | None = None,
    ) -> None:
        self.config = config
        self.label_config = label_config or LabelConfig.resolve(config)
        from beam_ai.training.tracker import ExperimentTracker

        self.tracker = tracker or ExperimentTracker()
        self.registry = registry or Registry()

    # ------------------------------------------------------------------ #

    def _build_dataloaders(self, splits):
        import torch
        from torch.utils.data import DataLoader

        tokenizer_pipeline = self.model.tokenizer_pipeline
        max_len = self.config.max_sequence_length

        def collate(batch):
            texts = [item[0] for item in batch]
            labels = torch.tensor([item[1] for item in batch], dtype=torch.long)
            encoded = tokenizer_pipeline.encode_batch(texts)
            return {**encoded, "labels": labels}

        generator = torch.Generator().manual_seed(self.config.random_seed)
        from beam_ai.training.data import build_sampler

        sampler = build_sampler(splits["train"].label_ids, self.config.sampling_strategy)
        shuffle = sampler is None  # WeightedRandomSampler replaces shuffling

        train_loader = DataLoader(
            list(zip(splits["train"].texts, splits["train"].label_ids)),
            batch_size=self.config.batch_size,
            shuffle=shuffle,
            sampler=sampler,
            generator=generator if shuffle else None,
            collate_fn=collate,
            num_workers=0,
        )
        val_loader = DataLoader(
            list(zip(splits["validation"].texts, splits["validation"].label_ids)),
            batch_size=max(1, self.config.batch_size * 2),
            shuffle=False,
            collate_fn=collate,
            num_workers=0,
        )
        return train_loader, val_loader

    def _evaluate_validation(self, val_loader) -> dict:
        y_true: list[int] = []
        y_pred: list[int] = []
        texts_all: list[str] = []
        labels_all: list[int] = []

        for batch in val_loader:
            labels_batch = batch.pop("labels")
            logits = self.model.forward_batch(
                batch["input_ids"], batch["attention_mask"]
            )
            preds = logits.argmax(dim=-1).tolist()
            y_pred.extend(preds)

        # Re-derive ground truth deterministically from the split order.
        for batch in val_loader:
            labels_all.extend(batch["labels"].tolist())

        # NOTE: iterating the loader twice keeps batching identical because
        # shuffle=False for the validation loader.
        y_true = labels_all
        from beam_ai.evaluation.metrics import compute_classification_metrics

        return compute_classification_metrics(y_true, y_pred, list(self.label_config.labels))

    def _class_weight_tensor(self):
        if self.config.class_weighting != "balanced":
            return None
        import torch

        counts: dict[int, int] = {}
        for label_id in self._train_label_ids:
            counts[label_id] = counts.get(label_id, 0) + 1
        total = len(self._train_label_ids)
        weights = [
            total / (len(counts) * counts.get(class_id, 0) or 1.0)
            for class_id in range(len(self.label_config.labels))
        ]
        return torch.tensor(weights, dtype=torch.float32)

    # ------------------------------------------------------------------ #

    def train(self) -> TrainResult:
        import torch
        from torch.nn import CrossEntropyLoss
        from torch.optim import AdamW

        try:
            from transformers import get_scheduler
        except ImportError:
            get_scheduler = None

        cfg = self.config
        started = time.perf_counter()

        device = resolve_device(cfg.device)
        set_seeds(cfg.random_seed)

        # 1. dataset -------------------------------------------------------
        from beam_ai.training.data import load_dataset_splits

        splits = load_dataset_splits(cfg, self.label_config)
        if not splits["train"] or splits["train"].label_ids is None:
            raise ValueError("Training split has no labeled rows; nothing to train on.")
        if not splits["validation"]:
            raise ValueError("Validation split is empty; refusing to train without it.")
        self._train_label_ids = list(splits["train"].label_ids)

        # 2. tokenizer + model ----------------------------------------------
        from beam_ai.models.factory import create_model
        from beam_ai.training.tokenization import TokenizerPipeline

        tokenizer = None
        if cfg.model_init == "tiny_random":
            # Offline, in-memory WordPiece tokenizer for plumbing runs.
            from beam_ai.training.offline import build_tiny_tokenizer

            tokenizer = TokenizerPipeline(
                build_tiny_tokenizer(), max_length=cfg.max_sequence_length
            )
        elif cfg.tokenizer_source:
            from transformers import AutoTokenizer

            tokenizer = TokenizerPipeline(
                AutoTokenizer.from_pretrained(cfg.tokenizer_source),
                max_length=cfg.max_sequence_length,
            )
        self.model = create_model(cfg, self.label_config, tokenizer=tokenizer)
        self.model.device = device
        self.model.hf_model.to(device)

        # 3. bookkeeping ------------------------------------------------------
        snapshot = cfg.to_serialisable()
        model_version = next_model_version(cfg.model_name, cfg.output_directory)
        snapshot["model_version"] = model_version
        run_id = self.tracker.new_run(
            model_name=cfg.model_name,
            dataset_version=cfg.dataset_version,
            config_snapshot=snapshot,
        )
        checkpoint_dir = cfg.output_directory / "checkpoints" / run_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.registry.register(
            model_name=cfg.model_name,
            model_version=model_version,
            task="emotion_classification",
            dataset_version=cfg.dataset_version,
            artifact_path="",
            status="training",
        )

        train_loader, val_loader = self._build_dataloaders(splits)

        # 4. optimization setup -------------------------------------------------
        no_decay = ("bias", "LayerNorm.weight")
        grouped_params = [
            {
                "params": [
                    p
                    for n, p in self.model.hf_model.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": cfg.weight_decay,
            },
            {
                "params": [
                    p
                    for n, p in self.model.hf_model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(grouped_params, lr=cfg.learning_rate)
        total_steps = max(1, len(train_loader)) * cfg.epochs
        scheduler = None
        if get_scheduler is not None:
            scheduler = get_scheduler(
                "linear",
                optimizer=optimizer,
                num_warmup_steps=int(cfg.warmup_ratio * total_steps),
                num_training_steps=total_steps,
            )
        loss_fn = CrossEntropyLoss(weight=self._class_weight_tensor())
        loss_fn.to(device)

        # 5. epochs -----------------------------------------------------------------
        best_f1 = -1.0
        best_epoch = 0
        best_state: dict | None = None
        best_val_metrics: dict | None = None
        global_step = 0

        for epoch in range(1, cfg.epochs + 1):
            epoch_started = time.perf_counter()
            self.model.hf_model.train()
            running_loss = 0.0
            batches = 0

            for batch in train_loader:
                labels_batch = batch.pop("labels")
                outputs = self.model.hf_model(
                    input_ids=batch["input_ids"].to(device),
                    attention_mask=batch["attention_mask"].to(device),
                )
                loss = loss_fn(outputs.logits, labels_batch.to(device))
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    self.model.hf_model.parameters(), cfg.gradient_clip_norm
                )
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                optimizer.zero_grad(set_to_none=True)

                running_loss += float(loss.detach())
                batches += 1
                global_step += 1

            train_loss = running_loss / max(1, batches)
            val_metrics = self._evaluate_validation(val_loader)
            epoch_duration = time.perf_counter() - epoch_started

            checkpoint_path = checkpoint_dir / f"epoch_{epoch:02d}.pt"
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": self.model.hf_model.state_dict(),
                    "val_metrics": {
                        k: v for k, v in val_metrics.items() if isinstance(v, (int, float))
                    },
                },
                checkpoint_path,
            )

            self.tracker.log_epoch(
                run_id,
                epoch=epoch,
                train_loss=train_loss,
                val_metrics=val_metrics,
                checkpoint_path=str(checkpoint_path),
                duration_seconds=epoch_duration,
            )

            if val_metrics["f1_macro"] > best_f1:
                best_f1 = val_metrics["f1_macro"]
                best_epoch = epoch
                best_val_metrics = val_metrics
                best_state = {
                    name: param.detach().cpu().clone()
                    for name, param in self.model.hf_model.state_dict().items()
                }

        # 6. final artifact (best epoch weights) ------------------------------
        if best_state is not None:
            self.model.hf_model.load_state_dict(best_state)
            self.model.hf_model.to(device)

        version_dir = artifact_dir_for(cfg.model_name, model_version, cfg.output_directory)
        final_metrics = {
            key: value
            for key, value in (best_val_metrics or {}).items()
            if isinstance(value, (int, float))
        }
        save_artifact(
            self.model,
            version_dir,
            training_config_snapshot=snapshot,
            dataset_version=cfg.dataset_version,
            metrics=final_metrics or None,
            status="training",
        )

        duration = time.perf_counter() - started
        self.tracker.finalize_run(
            run_id,
            status="completed",
            metrics=final_metrics or None,
            artifact_path=str(version_dir),
            duration_seconds=duration,
        )
        self.registry.register(
            model_name=cfg.model_name,
            model_version=model_version,
            task="emotion_classification",
            dataset_version=cfg.dataset_version,
            artifact_path=str(version_dir),
            status="training",
            created_at=None,
        )
        if final_metrics:
            # Real validation-split measurements -> validated (NOT production).
            self.registry.set_metrics(cfg.model_name, model_version, final_metrics)

        return TrainResult(
            run_id=run_id,
            model_name=cfg.model_name,
            model_version=model_version,
            artifact_dir=version_dir,
            best_epoch=best_epoch,
            best_val_metrics=best_val_metrics,
            duration_seconds=duration,
        )
