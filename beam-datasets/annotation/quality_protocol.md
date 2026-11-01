# B.E.A.M. Annotation Quality Protocol

Version: 1.0.0  
Status: Ratified  
Audience: Annotation leads, quality reviewers, research team  

This document defines the quality-control procedure for the B.E.A.M.
supervised emotion-annotation project.

The protocol is designed to support reliable, reproducible annotations at
scale while preserving the nuance required for emotion classification in
informal online text.

---

## 1. Annotation Team Structure

### 1.1 Roles

| Role | Responsibility |
|------|---------------|
| Annotation Lead | Owns the annotation workflow, trains annotators, monitors quality metrics, resolves disputes. |
| Annotator | Performs independent annotations according to the guidelines. |
| Adjudicator | Resolves disagreements. Should be senior or highly trained. Must not annotate records they previously annotated. |
| Quality Reviewer | Audits annotation quality on a sample basis and reports metrics to the lead. |

### 1.2 Minimum Team Size

For each annotation batch:

- **At least three annotators** should annotate every record when resources permit.
- For initial pilot batches, **two annotators** is acceptable, with adjudication for disagreements.
- For production batches, aim for **three annotators** with a fourth serving as adjudicator.

### 1.3 Annotator Independence

Annotators must work **independently**. They must not discuss records with
each other before submitting their annotations.

---

## 2. Annotation Procedure

### 2.1 Batch Preparation

1. The annotation lead selects a batch of unlabeled records from the
   dataset pipeline output.
2. Records are assigned to annotators through a blind allocation system
   where feasible.
3. Annotators receive:
   - The current taxonomy (`taxonomy.yaml`)
   - The annotation guidelines (`annotation_guidelines.md`)
   - The schema definition (`schema.json`)
   - A set of calibrated example annotations (`examples.jsonl`)
   - A brief training session or walkthrough

### 2.2 Independent Annotation

1. Each annotator independently reads and classifies each assigned record.
2. Annotations are submitted through the annotation interface (to be
   specified when the tooling is selected).
3. Annotators must complete all fields. `secondary_emotion` may be `null`.
4. Annotators must provide `notes` when `confidence` is 1 or when the case
   is ambiguous.
5. Annotators must not consult each other or use external AI tools to make
   classification decisions.

### 2.3 Blinding

Where technically feasible:

- Annotators should be blinded to the identities of other annotators
  assigned to the same records.
- The annotation tool should not display other annotators' labels during
  the annotation phase.

---

## 3. Disagreement Detection

### 3.1 Primary Label Agreement

After all annotators have submitted for a batch, the system computes
agreement on `primary_emotion`.

A record has **disagreement** when not all annotators assigned the same
`primary_emotion`.

### 3.2 Secondary Label Agreement

Secondary label agreement is computed only for records where at least one
annotator assigned a non-null `secondary_emotion`.

### 3.3 Intensity Agreement

Intensity agreement is measured as the absolute difference between
annotator intensity scores. Disagreement threshold: `|a - b| >= 2`.

### 3.4 Confidence Agreement

Low-confidence annotations (`confidence = 1` or `2`) are flagged for
adjudication regardless of label agreement.

---

## 4. Adjudication Procedure

### 4.1 When to Adjudicate

Adjudicate records where:

- `primary_emotion` labels disagree among annotators.
- Any annotator assigned `confidence = 1`.
- Intensity scores differ by 2 or more points.
- Any annotator flagged a high-risk context (`SELF_HARM_REFERENCE`,
  `THREAT_REFERENCE`, `VIOLENCE_REFERENCE`) that was not flagged by all
  annotators.

### 4.2 Adjudication Process

1. The adjudicator receives:
   - The original text
   - All independent annotations
   - The annotators' notes
   - The taxonomy and guidelines
2. The adjudicator must **not** be one of the original annotators for the
   disputed record.
3. The adjudicator independently reviews the text and all annotations.
4. The adjudicator selects a final `primary_emotion` and `secondary_emotion`.
5. The adjudicator may set `confidence` to any value based on their
   certainty.
6. The adjudicator records a note explaining the rationale for the
   decision, particularly when overriding a majority view.
7. The adjudicator should prefer the interpretation that is most
   consistent with the guidelines and taxonomy definitions.

### 4.3 Adjudicator Thresholds

| Disagreement Type | Action |
|-------------------|--------|
| All annotators agree on primary | No adjudication needed for primary label. |
| 2-of-3 agree on primary | Review notes; adjudicate if confidence is low or context differs. |
| All three disagree (3-way tie) | Mandatory adjudication. |
| Any confidence = 1 | Mandatory adjudication. |
| Intensity difference >= 2 | Review; adjudicator sets final intensity. |

---

## 5. Agreement Metrics

### 5.1 Primary Emotion: Cohen's Kappa

Compute Cohen's kappa (or Fleiss' kappa for three or more annotators) on
`primary_emotion` labels.

- **Target kappa:** 0.70 or higher for the full annotation set.
- **Acceptable kappa:** 0.60–0.69; triggers additional training and guideline review.
- **Insufficient kappa:** Below 0.60; halts annotation until guidelines or training are revised.

### 5.2 Per-Class Agreement

Report agreement metrics **per emotion class**. Some classes may be
systematically harder to annotate (e.g., distinguishing
NEUTRAL_ANALYTICAL from low-intensity APPREHENSION_ANXIETY).

### 5.3 Secondary Emotion Agreement

Report simple percentage agreement for `secondary_emotion`. Secondary
agreement is expected to be lower because `null` is a common value.

### 5.4 Intensity Correlation

Report the intraclass correlation coefficient (ICC) for `intensity` scores
across annotators.

### 5.5 Confidence Distribution

Report the distribution of `confidence` values. A high proportion of
`confidence = 1` annotations indicates guideline ambiguity that should be
resolved.

### 5.6 Context Flag Agreement

Report percentage agreement per context flag. Flags with low agreement
should be reviewed for clarity.

### 5.7 Threshold Table

| Metric | Target | Acceptable | Insufficient |
|--------|--------|------------|--------------|
| Cohen's / Fleiss' kappa (primary) | >= 0.70 | 0.60–0.69 | < 0.60 |
| ICC (intensity) | >= 0.75 | 0.60–0.74 | < 0.60 |
| Per-class kappa (worst class) | >= 0.60 | 0.50–0.59 | < 0.50 |
| Confidence-1 proportion | < 5% | 5–10% | > 10% |

### 5.8 Timing of Metrics Review

- **After pilot batch** (50–100 records): Full metrics review. Adjust
  guidelines or training if thresholds are not met.
- **After every 500 records**: Spot-check metrics review.
- **After full dataset annotation**: Final metrics report.

---

## 6. Handling Ambiguous Examples

### 6.1 Flag for Review

Any annotator may flag a record as ambiguous by setting `confidence = 1`
and providing a note.

### 6.2 Ambiguity Categories

Annotators should use the following categories in their notes when
relevant:

- **Mixed emotions**: Two or more emotions are clearly present at similar strength.
- **Context-dependent**: The meaning depends on subreddit culture, thread context, or prior posts that are not visible in the text.
- **Hyperbolic language**: Strong words are used figuratively rather than literally.
- **Irony / sarcasm**: The surface emotion contradicts the intended meaning.
- **Hypothetical / fictional**: The author is not describing their own experience.
- **Cultural or subcultural reference**: The text relies on shared context not visible to the annotator.

### 6.3 Ambiguity Resolution

1. All ambiguous records go to adjudication.
2. The adjudicator's decision is final for that record.
3. If a pattern of ambiguity emerges for a particular category, the
   guidelines should be updated and annotators retrained.

---

## 7. Label Revision Procedure

### 7.1 Post-Adjudication Review

After adjudication, the annotation lead should review a random sample of
10% of records for consistency with the guidelines.

### 7.2 Guideline Updates

If systematic disagreements are found:

1. The annotation lead convenes a meeting with annotators and the
   adjudicator.
2. The team reviews the specific records and identifies the source of
   confusion.
3. The guidelines (`annotation_guidelines.md`) and/or taxonomy
   (`taxonomy.yaml`) are updated with additional examples or clarified
   definitions.
4. Annotators are briefed on the changes.
5. Previously annotated records are **not** automatically relabeled unless
   the taxonomy itself changes.

### 7.3 Taxonomy Changes

Taxonomy changes (adding, removing, or renaming labels) require:

1. A documented rationale.
2. Approval from the research team.
3. A migration plan for previously annotated records.
4. Retraining of all annotators.

Taxonomy changes are expected to be rare.

---

## 8. Annotator Training and Calibration

### 8.1 Initial Training

Before annotating production data, all annotators must:

1. Read the taxonomy and annotation guidelines.
2. Complete a calibration exercise using the example annotations in
   `examples.jsonl`.
3. Discuss edge cases with the annotation lead.
4. Pass a calibration test: annotate 20 pre-calibrated records and
   achieve kappa >= 0.60 against the gold standard.

### 8.2 Ongoing Monitoring

- The annotation lead should periodically review each annotator's work
  for consistency.
- Annotators whose kappa falls below 0.60 in a batch should receive
  additional training before continuing.

### 8.3 Inter-Annotator Feedback

After each batch, annotators may submit feedback on:

- Guideline clarity
- Difficult edge cases
- Suggested examples for the guidelines

The annotation lead should review feedback and update guidelines as needed.

---

## 9. Data Retention and Audit Trail

### 9.1 Retention

All annotation records must be retained, including:

- Individual annotator submissions
- Adjudication records
- Agreement metrics
- Guideline revision history

### 9.2 Audit Trail

Each annotation record must contain:

- `annotator_id`
- `annotation_timestamp`
- `version` of the taxonomy and guidelines used

If the taxonomy or guidelines are revised, the version must be recorded
alongside the annotation so that the correct specification can be applied
during analysis.

### 9.3 Privacy

- `annotator_id` must be a stable pseudonym, not a real name.
- No personal information about annotators should be stored in the dataset.
- No personal information about the original Reddit authors should be
  stored in annotation records.

---

## 10. Quality Report Template

After each batch, the annotation lead should produce a quality report
containing:

- Batch identifier and size
- Number of annotators
- Primary emotion Cohen's / Fleiss' kappa
- Per-class kappa table
- Intensity ICC
- Confidence distribution
- Context flag agreement (top and bottom flags)
- Number of adjudicated records
- Adjudication rationale summary
- Guideline revisions made (if any)
- Annotator-level metrics (for internal quality monitoring only, not
  for publication)

---

## 11. Pilot Study Recommendation

Before annotating the full dataset, the team should conduct a pilot study:

1. Select 20–50 diverse records from the unlabeled dataset.
2. Have 3 annotators independently annotate them.
3. Compute agreement metrics.
4. Hold a discussion to identify systematic disagreements.
5. Revise guidelines if necessary.
6. Repeat until kappa >= 0.70 is achieved.

The pilot study should be documented and included in any research
publication describing the annotation process.

---

## 12. Non-Goals

This quality protocol does **not** cover:

- Clinical validation of the taxonomy
- Cross-cultural reliability
- Automated pre-labeling or active learning
- Annotation tool selection or implementation (to be specified separately)

The protocol is designed for **human annotation of informal English text**
from public Reddit content.
