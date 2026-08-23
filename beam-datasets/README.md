# B.E.A.M. Datasets

This directory stores the dataset lifecycle for the Behavioral Emotion
Analysis Model research project.

- `raw/`: Source data exactly as collected (untouched).
- `processed/`: Cleaned and transformed datasets.
- `external/`: External reference data and imports.
- `exports/`: Read-only exports produced by `beam-scraper/scripts/export_data.py`
  (`csv` / `jsonl`, timestamped filenames).

The collection tooling lives in [`../beam-scraper`](../beam-scraper).

---

## Dataset structure

Two tables back every export, written by the Reddit ingestion pipeline:

### `reddit_posts`

| Field | Type | Definition |
|---|---|---|
| `reddit_post_id` | string (unique) | Reddit base36 submission ID — stable join key |
| `subreddit` | string | Subreddit display name |
| `title` | text | Post title as displayed |
| `body` | text, nullable | Self-text; NULL when unavailable (see body_status) |
| `body_status` | enum | `available` / `removed` / `deleted` / `empty` |
| `author` | string, nullable | **Anonymized** author pseudonym (HMAC-SHA256, salted, 16 hex chars). Raw handles are never persisted. NULL if deleted/suspended |
| `created_utc` | timestamptz | Post creation time (UTC) |
| `score` | int | Net score at retrieval time |
| `upvote_ratio` | float | 0–1 ratio at retrieval time |
| `num_comments` | int | Comment count at retrieval time |
| `url` / `permalink` | text | Link target / canonical permalink |
| `is_nsfw` / `is_spoiler` / `stickied` | bool | Content flags |
| `retrieved_at` | timestamptz | When our collector stored the row (kept from first insert) |
| `updated_at` | timestamptz, nullable | Last metadata refresh |

### `reddit_comments`

| Field | Type | Definition |
|---|---|---|
| `reddit_comment_id` | string (unique) | Reddit base36 comment ID |
| `post_id` | string (FK) | Parent `reddit_posts.reddit_post_id` (cascade delete) |
| `parent_id` | string, nullable | Immediate parent comment or post ID |
| `depth` | int | Nesting depth (top-level = 0) |
| `subreddit` | string | Denormalized for query convenience |
| `body` / `body_status` / `author` | — | Same semantics as posts |
| `created_utc` / `score` / `retrieved_at` / `updated_at` | — | Same semantics as posts |

**Not stored**: emails, real names, profile descriptions, private
messages, voting behavior of identifiable users, or any private account
data.

## Source

Public Reddit content from subreddits configured in the scraper
(defaults: `AskReddit`, `CasualConversation`; fully configurable via the
`SUBREDDITS` environment variable). Access is via Reddit's official API
(PRAW, read-only script application) in compliance with their terms and
rate limits.

## Collection date

Per-record: `retrieved_at` (first collection) and `updated_at` (latest
refresh) are stored on every row. Export files carry a UTC timestamp in
their filename (`posts_YYYYMMDD_HHMMSS.csv`). No dataset-wide snapshot
date exists by design — data accumulates across runs.

## Collection method

1. `scripts/scrape_subreddit.py` walks a listing (`hot/new/top/rising`,
   optional time filter for `top`) with a configured post limit.
2. For each parsed post, `scripts/scrape_post.py` logic collects the
   nested comment tree ("load more" stubs expanded, depth tracked).
3. Records pass through a validation/parsing layer that flags
   `[removed]`/`[deleted]` bodies and drops unusable items with logged
   errors.
4. Storage deduplicates by Reddit ID (insert-or-update).
5. `scripts/export_data.py` streams rows to CSV/JSONL without modifying
   the database.

Rate limiting: minimum interval between API calls plus exponential
backoff on transient failures; strictly sequential requests.

## Limitations

* **Snapshot bias** — scores/ratios reflect retrieval time only.
* **Deletion drift** — content removed between post creation and
  collection appears as `removed/deleted` status, not original text.
* **Listing bias** — hot/top/rising over-represent popular content;
  combine modes and time filters to mitigate.
* **Comment truncation** — per-post comment limits may cut deep trees;
  `depth` lets downstream users account for this.
* **No historical edits** — edited bodies are stored as last-seen.
* **Subreddit scope** — dataset composition reflects configured
  subreddits, not Reddit overall.

## Ethical considerations

* Only publicly accessible content is collected, via the official API.
* The dataset is used for emotion-expression research on *text*, never to
  profile, identify, or contact individual users.
* Author handles are never stored — only salted pseudonyms, retained
  solely for deduplication
  and thread integrity; they must not be published in derived corpora.
* Deleted/removed content is recorded as a status, respecting user
  deletion intent; original text is never recoverable or guessed.
* NSFW/spoiler/stickied flags allow filtered downstream use.
* This pipeline does **not** implement diagnosis or psychological
  assessment of individuals.

## Data cleaning requirements (downstream)

1. Filter or impute `body_status != 'available'` rows per experiment.
2. Deduplicate near-duplicate crossposts manually (Reddit IDs handle
   exact duplicates already).
3. Normalize whitespace/encoding; consider markdown stripping.
4. Remove bot-generated content as needed (bot pseudonyms cannot be
   detected by name suffix anymore — filter by repeated low-effort bodies
   or known subreddit bot lists instead).
5. Re-check `stickied` moderation posts before including in analysis.
6. Split train/validation/test by `reddit_post_id` hash to avoid leakage
   across comments of one thread.
