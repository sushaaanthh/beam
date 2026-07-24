# Setup

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ for the frontend
- Python 3.11+ for the backend and AI services

## Local Development

### API

```bash
cd beam-api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Web

```bash
cd beam-web
npm install
npm run dev
```

## Docker

```bash
docker compose up --build
```

The default services are `postgres`, `beam-api`, and `beam-web`.