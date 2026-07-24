# B.E.A.M.
### Behavioral Emotion Analysis Model

B.E.A.M. is an explainable AI framework that detects and analyzes hedonic emotional states through transformer-based behavioral analysis of online users. The platform combines Natural Language Processing, Deep Learning, Behavioral Analytics, and Explainable AI to generate interpretable psychological insights from online textual behavior.

## Project Overview

B.E.A.M. is organized as a modular workspace so the API, web client, AI workflows, scraper scaffold, datasets, and trained models can evolve independently without sharing implementation concerns.

## Architecture

- `beam-api/`: FastAPI backend, database access, and Alembic migrations.
- `beam-web/`: React + Vite frontend with TailwindCSS, React Router, and Axios ready for UI work.
- `beam-ai/`: Training, inference, preprocessing, evaluation, explainability, and notebook workspace.
- `beam-scraper/`: Independent Reddit ingestion scaffold for future data collection.
- `beam-config/`: Shared prompts, environment templates, constants, labels, and settings.
- `beam-datasets/`: Raw, processed, external, and export datasets.
- `beam-models/`: Checkpoints, production models, and experiments.
- `docs/`: Architecture, setup, roadmap, and API documentation.

## Folder Structure

```text
beam/
├── beam-api/
├── beam-web/
├── beam-ai/
├── beam-scraper/
├── beam-config/
├── beam-datasets/
├── beam-models/
├── docs/
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Tech Stack

- Frontend: React, Vite, TailwindCSS, React Router, Axios
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic Settings, Uvicorn, PostgreSQL
- AI/ML: PyTorch, HuggingFace Transformers, spaCy, scikit-learn
- Infrastructure: Docker, Docker Compose

## Installation

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ for local frontend development
- Python 3.11+ for local backend or AI development

### Repository Setup

```bash
docker compose version
node --version
python --version
```

## Running Locally

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

## Docker Setup

Start the full stack from the repository root:

```bash
docker compose up --build
```

Services exposed by default:

- Web UI: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Future Roadmap

- Add the AI training pipelines under `beam-ai/`.
- Implement Reddit ingestion in `beam-scraper/`.
- Expand explainability outputs and persistence.
- Add model versioning, evaluation, and experiment tracking.
- Document and automate deployment workflows.

## Contributing

1. Create a feature branch.
2. Keep changes scoped to the relevant service or shared config.
3. Update docs when structure or behavior changes.
4. Run the relevant build or validation command before opening a pull request.

## License

No license has been published yet. Add one before external distribution.
