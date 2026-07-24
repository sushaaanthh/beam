# B.E.A.M. Backend

FastAPI backend for B.E.A.M. built with SQLAlchemy 2.0, PostgreSQL, Alembic, and Pydantic v2.

## Stack

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Pydantic v2 / Pydantic Settings
- Uvicorn
- Python 3.11

## Project Layout

```text
beam-api/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── database/
│   ├── exceptions/
│   ├── main.py
│   ├── middleware/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── alembic/
├── tests/
├── .env.example
├── Dockerfile
└── requirements.txt
```

## Environment Setup

1. Copy `.env.example` to `.env` and adjust the values for your environment.
2. Ensure PostgreSQL is running and reachable from the backend.
3. Install the authentication dependencies listed in `requirements.txt` before running the app.
4. Import the Postman collection from `postman/B.E.A.M.-auth.postman_collection.json` to try the auth endpoints quickly.

## Run Locally

```bash
cd beam-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

From the repository root:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Database Migrations

Create and apply Alembic migrations after adding models:

```bash
alembic revision --autogenerate -m "create initial schema"
alembic upgrade head
```

## Endpoints

- `GET /` returns the project status.
- `GET /api/v1/health` checks API and database connectivity.
- `POST /api/v1/auth/register` creates a user account.
- `POST /api/v1/auth/login` returns access and refresh JWTs.
- `POST /api/v1/auth/refresh` rotates JWT access tokens.
- `POST /api/v1/auth/logout` revokes the current JWT and any provided refresh token.
- `GET /api/v1/users/me` returns the authenticated user.

## Notes

- JWT configuration is driven by `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, and `JWT_ISSUER`.
- JWT settings are loaded from environment variables in `app/core/config.py`.
- The authorization middleware rejects invalid or expired bearer tokens before protected endpoints execute.
- AI, scraping, and other future modules should be added behind the versioned API and service layer.
