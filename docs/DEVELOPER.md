# Developer Guide

## Prerequisites

Use Python 3.12 or newer, PostgreSQL 16 for production-like work, Redis 7 for shared rate-limit storage, Git, and Docker Desktop when running the local service stack. SQLite is sufficient for the default development test path.

## Setup

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
alembic upgrade head
pytest -v
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
pytest -v
```

Set `DATABASE_URL` to PostgreSQL for integration work. Keep `SECRET_KEY` at least 32 characters.

## Adding an Entity

1. Copy `app/models/domain/product.py` to a new model module and customize columns, constraints, indexes, and ownership.
2. Add matching Pydantic schemas under `app/models/schemas/`.
3. Import the model in `app/models/__init__.py` so Alembic sees it.
4. Add a repository for query composition and persistence.
5. Add service methods for business rules and transaction boundaries.
6. Add versioned endpoint routes and register the router in `api_router.py`.
7. Generate and review a migration: `alembic revision --autogenerate -m "add_orders"`.
8. Apply it locally with `alembic upgrade head` and add unit/integration tests.

## Migrations

```bash
alembic current
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
alembic downgrade -1
```

Review generated SQL and use batch operations when a SQLite development migration changes constraints. Production migrations should run as a separate deployment step before application rollout.

## Testing and Quality

```bash
pytest -v
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=80
ruff check app scripts
black --check app scripts
isort --check-only app scripts
mypy app
```

Unit tests use mocks for service boundaries. Integration tests use an isolated async SQLite schema through `app/tests/conftest.py`.

## Code Style

Black and isort are configured in `pyproject.toml`. Ruff uses a 120-character line length and ignores FastAPI's intentional `Depends()` default pattern. Keep public functions typed, preserve the response envelope, and document non-obvious security or transaction logic.

## Common Tasks

- New endpoint: add a route in the appropriate `api/v1/endpoints` module, inject dependencies, validate a schema, and return `APIResponse`.
- New table: create a mapped model, add relationships/back-populates, register it, generate a migration, and test it.
- New service method: keep domain decisions in `services/`, accept explicit dependencies, and test success/failure paths.
- New repository method: use SQLAlchemy expressions with bound parameters, bound limits, and deterministic ordering.
- New dependency: add it to both `requirements.txt` and `pyproject.toml`; add development-only packages to `requirements-dev.txt`.

## Debugging

Run `uvicorn app.main:app --reload --log-level debug` locally. Inspect `/docs`, `/health`, and Loguru's rotating `logs/app.log`. Never log passwords, raw refresh tokens, OAuth secrets, or reset/verification tokens.

## Troubleshooting

- `SECRET_KEY` validation error: set a non-default value of at least 32 characters in `.env`.
- `no such table`: run `alembic upgrade head` against the same `DATABASE_URL` used by the process.
- SMTP connection failure: configure `SMTP_HOST`, `SMTP_PORT`, credentials, and `EMAIL_FROM`; development mode skips delivery when no SMTP user is configured.
- OAuth callback failure: verify provider redirect URIs exactly match the configured public URL and provide client credentials.
- PostgreSQL connection failure: confirm the async URL uses `postgresql+asyncpg://` and that the service is healthy.
- Rate-limit storage across replicas: configure a shared SlowAPI/Redis backend rather than relying on process-local state.
