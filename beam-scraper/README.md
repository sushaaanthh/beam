# B.E.A.M. Reddit Data Ingestion Pipeline

Collects **publicly available** Reddit posts and comments for research
dataset construction. This is a pure data-collection layer: it contains no
AI, no emotion classification, no psychological inference and no user
profiling.

The scraper is independent of `beam-web`, `beam-ai` and `beam-api`. It
shares only a PostgreSQL instance (via its own `DATABASE_URL`) and writes
to its own tables (`reddit_posts`, `reddit_comments`).

---

## Setup

```bash
cd beam-scraper
python -m venv .venv && .venv\Scripts\activate     # Windows; use source .venv/bin/activate on POSIX
pip install -r requirements.txt                    # Python 3.11+

copy .env.example .env                             # then fill in real values
```

Create Reddit API credentials at <https://www.reddit.com/prefs/apps>
(application type **script**). The user agent must identify the research
use case, e.g. `windows:beam-research-scraper:v1.0 (by /u/your_name)`.

> `.env` is git-ignored. Never commit credentials or tokens.

## Usage

```bash
# newest posts
python scripts/scrape_subreddit.py --subreddit AskReddit --limit 50 --sort new

# top posts from the last month
python scripts/scrape_subreddit.py --subreddit AskReddit --limit 50 --sort top --time-filter month

# several subreddits, no comments, custom comment cap
python scripts/scrape_subreddit.py --subreddit AskReddit CasualConversation --limit 25 --no-comments

# one thread by id or URL
python scripts/scrape_post.py --post-id abc123 --subreddit AskReddit
python scripts/scrape_post.py --url https://www.reddit.com/r/CasualConversation/comments/abc123/title/

# export collected data (read-only)
python scripts/export_data.py --format csv --subreddit AskReddit --limit 100
python scripts/export_data.py --format jsonl --comments
```

Sort modes: `hot | new | top | rising` — time filters (`--time-filter`,
used with `top`): `day | week | month | year | all`.

Defaults come from environment variables (`SUBREDDITS`, `POST_LIMIT`,
`COMMENT_LIMIT`, `SCRAPE_SORT`, `TIME_FILTER`, `INCLUDE_COMMENTS`) so any
subreddit list can be configured without code changes.

Exports are written to `../beam-datasets/raw/` by default (timestamped
filenames, read-only against the database).

## Architecture

```
config/settings.py      Pydantic Settings (env-driven configuration)
reddit/client.py        PRAW wrapper: auth, read-only mode, validation (no scraping logic)
reddit/rate_limit.py    min request interval + exponential backoff retries
reddit/schemas.py       typed PostRecord / CommentRecord + parsing & content-quality flags
reddit/post_collector.py   hot/new/top/rising listing collection
reddit/comment_collector.py nested comment-tree collection (depth tracked)
reddit/collector.py     orchestrator producing a structured ScrapeSummary
reddit/models.py        SQLAlchemy models (reddit_posts / reddit_comments)
reddit/storage.py       deduplicating upserts + read-only export queries
scripts/                CLI entry points (scrape_subreddit, scrape_post, export_data)
tests/                  pytest suite with mocked Reddit objects (no live API)
logs/                   rotating JSON log (git-ignored)
```

## Deduplication

Reddit IDs are unique keys:

* unknown ID → insert;
* known ID → update mutable metadata only (score, counts, body
  availability, flags). The first `retrieved_at` is preserved,
  `updated_at` refreshed. Duplicates are never created.

## Data-quality handling

| Situation | Behavior |
|---|---|
| `[removed]` / `[deleted]` body | stored as NULL with `body_status` = `removed` / `deleted` |
| empty body (link/image posts) | `body_status = empty` |
| deleted author | author stored as NULL |
| malformed record (no id/title) | logged as `*_parse_skipped`, run continues |
| API failure / rate limit | exponential backoff (429/5xx/network), then graceful stop with summary |
| storage error | per-record SAVEPOINT rollback; batch survives |

Every run logs: start, subreddit, requested/stored/duplicate/comment
counts, errors and duration (JSON lines in `logs/scraper.log`).
Credentials never appear in logs.

## Rate limiting & etiquette

* sequential collection only — no concurrent bursts;
* minimum interval between Reddit calls (default 1.1 s);
* exponential backoff on transient errors;
* PRAW's built-in throttling remains active underneath.

## Privacy decisions (research data minimization)

Collected **only**: post/comment text and public metadata needed for the
dataset (ids, subreddit, timestamps, scores, ratios, flags, permalinks).

**Authors are anonymized, not stored.** The public handle is replaced at
parse time by a deterministic salted pseudonym (HMAC-SHA256, first 16 hex
chars; salt via `AUTHOR_HASH_SALT`). This preserves within-dataset
capabilities (deduplication, per-author thread integrity) while making the
original handle unrecoverable from the stored value alone. Deleted or
suspended authors are stored as NULL.

Never collected: emails, real names, profile descriptions, private
messages, follower/friend graphs, location, or any private account
information. Deleted/removed content is preserved *as a status flag*
rather than silently dropped, which keeps the dataset honest about what
was visible at collection time.

## Testing

```bash
pytest            # unit tests; mocked Reddit, no credentials required
```
