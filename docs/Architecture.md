# Architecture

B.E.A.M. is split into independently deployable and maintainable service areas.

## Services

- `beam-api/`: FastAPI application, database access, and Alembic migrations.
- `beam-web/`: React frontend built with Vite.
- `beam-ai/`: Training, inference, preprocessing, evaluation, and explainability workflows.
- `beam-scraper/`: Independent Reddit collection scaffold for future ingestion jobs.
- `beam-datasets/`: Raw, processed, external, and exported datasets.
- `beam-models/`: Checkpoints, production models, and experiment artifacts.

## Flow

1. Data is collected by the scraper module.
2. Data is stored in the dataset layer after validation and preprocessing.
3. AI pipelines train and evaluate models from the curated data.
4. The backend exposes API endpoints for application and model integration.
5. The frontend consumes the API and surfaces interpretable results.