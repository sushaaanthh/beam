# Deployment

Production topology:

- `beam-web/` -> Vercel (static Vite build)
- `beam-api/` -> Render Web Service (Docker)
- PostgreSQL -> Render Postgres (or Neon)

## 1. Repository changes required for production

These are already applied in this repository:

- `beam-api/requirements.txt` includes the runtime-only dependencies
  (`dnspython`, `SpeechRecognition`, `reportlab`) and excludes unused ML
  packages (`torch`, `transformers`, `spacy`, `scikit-learn`).
- `beam-api/Dockerfile` binds Uvicorn to Render's `$PORT`.
- `beam-api/app/core/config.py` normalises `postgres://`,
  `postgresql://`, and `postgresql+psycopg://` URLs to the
  `postgresql+psycopg2://` SQLAlchemy dialect.
- `beam-api/.dockerignore` keeps `.env`, the local SQLite file, caches, and
  tests out of the image.
- `beam-web/vercel.json` provides the SPA rewrite to `index.html`.
- `render.yaml` is an optional Render Blueprint for the API and database.

## 2. Deploy the API on Render

### Option A: Blueprint (recommended for a fresh setup)

1. Push this repository to GitHub.
2. Render Dashboard -> **New +** -> **Blueprint**.
3. Select the repository. Render reads `render.yaml`.
4. When prompted, paste the Neon `DATABASE_URL` (or the Render Postgres URL).
5. Enter `GEMINI_API_KEY` when prompted (or leave it blank; the API falls back
   to lexicon analysis).
6. After the first deploy, replace `BACKEND_CORS_ORIGINS` with the real Vercel
   URL (see step 4).

### Option B: Manual

1. Render Dashboard -> **New +** -> **PostgreSQL**.
   - Name: `beam-postgres`
   - Database: `beam_db`
   - User: `beam`
   - Region: Oregon (use the same region for the API)
2. Copy the **Internal Database URL**.
3. Render Dashboard -> **New +** -> **Web Service**.
   - Repository: this repo
   - Root Directory: `beam-api`
   - Runtime: Docker
   - Dockerfile Path: `./Dockerfile`
   - Health Check Path: `/api/v1/health`
   - Region: Oregon
4. Add environment variables:

   | Key | Value |
   | --- | --- |
   | `ENVIRONMENT` | `production` |
   | `DEBUG` | `false` |
   | `LOG_LEVEL` | `INFO` |
   | `DATABASE_URL` | Internal Database URL from step 2 |
   | `JWT_SECRET_KEY` | output of `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `JWT_ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
   | `REFRESH_TOKEN_EXPIRE_DAYS` | `14` |
   | `JWT_ISSUER` | `beam-api` |
   | `BACKEND_CORS_ORIGINS` | `["https://your-project.vercel.app"]` |
   | `GEMINI_API_KEY` | optional |
   | `GEMINI_MODEL` | `gemini-3.1-flash-lite` |

5. Before the first deploy, run the migrations from your machine using the
   **External Database URL** from the Render database page:

   ```powershell
   pip install -r beam-api/requirements.txt
   $env:DATABASE_URL = "<external-database-url>"
   cd beam-api
   python -m alembic upgrade head
   ```

   On startup, `Base.metadata.create_all` adds `journals` and `reddit_cache`,
   which are not yet covered by an Alembic revision.

6. Deploy. The service is live when `/api/v1/health` returns
   `{"status":"healthy","database":"connected"}`.

### If the API already booted before migrations

`create_all` creates the schema on first boot. Running `upgrade head` after that
fails with "relation already exists". In that case baseline once instead:

```powershell
$env:DATABASE_URL = "<external-database-url>"
cd beam-api
python -m alembic stamp head
```

Use `upgrade head` for every future revision.

## 3. Deploy the frontend on Vercel

1. Vercel -> **Add New Project** -> import this repository.
2. Configure:
   - Root Directory: `beam-web`
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm ci`
3. Add environment variable:
   - `VITE_API_URL` = `https://<render-service>.onrender.com`
   - Scope: Production, Preview, Development
4. Deploy. `beam-web/vercel.json` handles client-side routes.

`VITE_API_URL` is baked into the bundle at build time. Changing it requires a
redeploy, and it must not include `/api/v1` or a trailing slash.

## 4. Connect the two services

In Render, set:

```
BACKEND_CORS_ORIGINS = ["https://your-project.vercel.app"]
```

The value must be valid JSON (double quotes, square brackets). Do not use `*`
while `allow_credentials=True` is enabled. Save; Render redeploys.

## 5. Verification

```powershell
curl -i https://<render-service>.onrender.com/api/v1/health
curl -i -X OPTIONS https://<render-service>.onrender.com/api/v1/auth/login `
  -H "Origin: https://your-project.vercel.app" `
  -H "Access-Control-Request-Method: POST"
```

Then in the browser: register, log in, open the dashboard, create an analysis,
and refresh a deep link such as `/dashboard` to confirm the SPA rewrite.

## 6. Custom domains

1. Vercel -> Project -> Settings -> Domains -> add `beam.example.com`.
2. Render -> API service -> Settings -> Custom Domains -> add
   `api.example.com`.
3. Update both:
   - Vercel: `VITE_API_URL=https://api.example.com`, redeploy.
   - Render: `BACKEND_CORS_ORIGINS=["https://beam.example.com"]`, redeploy.

## 7. Before public launch

- `POST /api/v1/auth/send-otp` returns the OTP in its response. Replace it with
  email delivery before exposing password reset to real users.
- Voice notes, chat history, notifications, OTPs, and the JWT blacklist are
  in memory. They are lost on restart and are not shared across instances.
- User-scoped routers such as journal, chat, voice, wellness, dashboard,
  social, reports, notifications, and privacy do not require authentication.
  Add `Depends(get_current_user)` before public traffic.
- Add rate limiting to `/auth/login` and `/auth/reset-password`.
- Render free web services sleep after inactivity; free Postgres instances
  expire. Upgrade before launch.
