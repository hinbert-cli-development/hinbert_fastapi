# Hinbert FastAPI

A modern, production-oriented FastAPI backend foundation for secure web applications. Built for teams that want a clean architecture, strong authentication defaults, scalable API design, and quick deployment without starting from scratch.

## Why this project?

Hinbert FastAPI combines a pragmatic backend structure with security-first design patterns:

- JWT-based authentication with refresh token rotation
- Password reset and email verification flows
- Optional TOTP multi-factor authentication
- OAuth login for Google and Facebook
- Async SQLAlchemy data layer with PostgreSQL support
- Rate limiting, request logging, and structured error handling
- Clean separation between API, services, repositories, and models
- Docker-ready local environment and deployment support

## Features

- Secure user registration and login
- Email verification and password recovery
- Access token + refresh token issuance
- Logout and refresh-token revocation
- TOTP setup and validation
- Social authentication hooks
- Product CRUD endpoints with filtering, sorting, and pagination
- Redis-backed rate limiting
- Pydantic-based validation and environment configuration
- Alembic migrations for database evolution
- Python testing coverage for core business flows

### Available Commands

| Command | Description | Example |
| --- | --- | --- |
| `hinbert init [PROJECT_NAME]` | Create a new FastAPI project | `hinbert init my_app` |
| `hinbert init --help` | Show help and available options | `hinbert init --help` |
| `hinbert init .` | Generate project in current directory | `hinbert init .` |
| `hinbert init [PROJECT_NAME] --yes` | Skip prompts, use defaults | `hinbert init my_app --yes` |
| `--db [postgresql|mysql|sqlite]` | Choose database | `--db postgresql` |
| `--auth [jwt|oauth2|none]` | Choose authentication | `--auth jwt` |
| `--no-2fa` | Skip two-factor authentication | `--no-2fa` |
| `--no-email` | Skip email verification | `--no-email` |
| `--no-rate-limit` | Skip rate limiting | `--no-rate-limit` |
| `--no-docker` | Skip Docker configuration | `--no-docker` |
| `--k8s` | Include Kubernetes/Helm | `--k8s` |
| `--logging [loguru|structlog|none]` | Choose logging library | `--logging structlog` |
| `-y, --yes` | Skip all confirmation prompts | `-y` |

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2 with async support
- PostgreSQL / SQLite compatibility
- Pydantic v2
- Redis
- Alembic
- JWT + bcrypt + pyotp
- Docker and Docker Compose
- pytest

## Architecture

```text
app/
├── api/
│   ├── deps/
│   └── v1/
│       ├── endpoints/
│       └── routers/
├── core/
│   ├── config/
│   ├── exceptions/
│   ├── middleware/
│   └── security/
├── db/
│   └── migrations/
├── models/
│   ├── domain/
│   └── schemas/
├── repositories/
├── services/
├── tests/
├── main.py
├── __init__.py

scripts/
├── create_admin.py
├── run_migrations.py
├── seed_data.py

docker/
├── Dockerfile
├── docker-compose.yml

alembic.ini
pyproject.toml
requirements.txt
requirements-dev.txt
.env.example
README.md
```

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL or Docker
- Redis or Docker
- Git

### 1. Clone the repository

```bash
git clone <repository-url>
cd hinbert_fastapi
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env
```

or:

```bash
cp .env.example .env
```

Update the values in `.env` for your database, Redis, JWT secret, SMTP settings, and OAuth credentials.

### 5. Run database migrations

```bash
python -m scripts.run_migrations
```

### 6. Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, the app is available at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

## Docker Setup

This project includes a Docker Compose setup for local development.

```bash
docker compose -f docker/docker-compose.yml up --build
```

To stop it:

```bash
docker compose -f docker/docker-compose.yml down
```

## API Highlights

The application exposes a versioned API under `/api/v1`.

### Auth endpoints

- `/api/v1/auth/signup`
- `/api/v1/auth/login`
- `/api/v1/auth/refresh`
- `/api/v1/auth/logout`
- `/api/v1/auth/forgot-password`
- `/api/v1/auth/reset-password`
- `/api/v1/auth/totp/setup`
- `/api/v1/auth/totp/verify`
- `/api/v1/auth/google`
- `/api/v1/auth/facebook`

### Product endpoints

- `/api/v1/products`
- `/api/v1/products/{product_id}`

### User endpoints

- `/api/v1/users/me`
- admin/user management routes where applicable

## Example Authentication Flow

```json
{
  "email": "user@example.com",
  "password": "StrongPassword!123"
}
```

The login response returns both an access token and refresh token:

```http
Authorization: Bearer <access_token>
```

## Environment Configuration

The project reads configuration using Pydantic settings from `.env` and supports values such as:

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `SMTP_HOST`
- `SMTP_PORT`
- `EMAIL_FROM`
- `GOOGLE_CLIENT_ID`
- `FACEBOOK_CLIENT_ID`
- `BACKEND_CORS_ORIGINS`

## Testing

Run the test suite with:

```bash
pytest
```

Targeted test folders:

```bash
pytest app/tests/unit
pytest app/tests/integration
```

## Security Notes

This project includes strong defaults for a starter backend, but production deployments should still:

- replace the default JWT secret with a secure secret manager value
- restrict CORS origins to trusted domains
- protect database credentials and infrastructure endpoints
- use HTTPS behind a reverse proxy or load balancer
- configure valid SMTP and OAuth provider credentials
- enable monitoring, backups, and secure deployment policies

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support

If you find this useful, please give it a ⭐ on GitHub!


