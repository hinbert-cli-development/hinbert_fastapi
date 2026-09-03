# Database Guide

## PostgreSQL Setup

Use PostgreSQL 16 or newer and create an application database/user with only the privileges required by the service. Configure:

```env
DATABASE_URL=postgresql+asyncpg://app_user:password@db-host:5432/app
```

The application uses async SQLAlchemy. SQLite with `sqlite+aiosqlite:///./test.db` is convenient for local development and tests, but PostgreSQL is the production target.

## Schema

| Table | Columns and constraints | Indexes |
|---|---|---|
| `users` | UUID `id` PK; `email` varchar(320) unique not null; `full_name` varchar(200) not null; `password_hash` varchar(255) not null; `is_active`, `is_admin`, `is_verified` booleans; UTC `created_at`, `updated_at` | Unique `email` |
| `products` | UUID `id` PK; `name` varchar(200) not null; `description` text; `price` numeric(12,2); `category` varchar(100); nullable `owner_id` FK to `users.id` with SET NULL; UTC audit fields | `name`, `category`, `owner_id` |
| `refresh_tokens` | UUID `id` PK; `user_id` FK CASCADE; `token_hash` varchar(64) unique; `expires_at`; nullable `revoked_at`; UTC audit fields | Unique `token_hash`, `user_id` |
| `email_verifications` | UUID `id` PK; `user_id` FK CASCADE; unique `token_hash` varchar(64); `expires_at`; nullable `used_at`; UTC audit fields | Unique `token_hash` |
| `password_resets` | UUID `id` PK; `user_id` FK CASCADE; unique `token_hash` varchar(64); `expires_at`; nullable `used_at`; UTC audit fields | Unique `token_hash` |
| `totp_secrets` | `user_id` PK/FK CASCADE; `encrypted_secret` varchar(512) not null | Primary key `user_id` |

UUID and datetime types are emitted by SQLAlchemy for the configured dialect. Inspect generated migration SQL before applying it to a production database.

## Relationships

```mermaid
erDiagram
    USERS ||--o{ REFRESH_TOKENS : owns
    USERS ||--o{ EMAIL_VERIFICATIONS : receives
    USERS ||--o{ PASSWORD_RESETS : requests
    USERS ||--o| TOTP_SECRETS : configures
    USERS ||--o{ PRODUCTS : owns
```

Token rows cascade when a user is deleted. Product ownership is nullable and becomes NULL when the owner is removed.

## Migrations

```bash
alembic current
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
alembic downgrade -1
```

The current migration chain is in `app/db/migrations/versions/`. `env.py` imports `app.models` so Alembic sees all mapped tables. SQLite constraint changes use batch operations.

## SQLAlchemy Models

Models are in `app/models/domain/`: `user.py`, `product.py`, `refresh_token.py`, `email_verification.py`, `password_reset.py`, and `totp_secret.py`. `base.py` supplies UUID identity and UTC audit timestamps. API schemas are separate under `app/models/schemas/`.

## Indexing Strategy

Email and token hashes are unique lookup indexes. Product name/category/owner indexes support collection filtering and ownership checks. Add indexes only for measured query patterns; use PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` before optimizing high-volume queries.
