# Deployment Guide

## Production Environment

Provide `DATABASE_URL` with `postgresql+asyncpg://`, a randomly generated `SECRET_KEY` of at least 32 characters, trusted `BACKEND_CORS_ORIGINS`, SMTP settings for email workflows, and OAuth credentials when social login is enabled. Store secrets in a cloud secret manager or Kubernetes Secret, not in Git.

## Docker

Build and run the image:

```bash
docker build -f docker/Dockerfile -t hinbert-fastapi:0.1.0 .
docker run --env-file .env -p 8000:8000 hinbert-fastapi:0.1.0
```

The image uses a builder and final stage, compiles Python bytecode, runs as UID 10001, exposes port 8000, and checks `/health` with Docker `HEALTHCHECK`.

## Docker Compose

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
alembic upgrade head
docker compose -f docker/docker-compose.yml up --build app
```

PostgreSQL uses `pg_isready`; Redis uses `redis-cli ping`. The app waits for both services to become healthy. Use a production secret manager instead of the local `.env` workflow.

## Kubernetes and Helm

The chart is under `docker/kubernetes`:

```bash
helm upgrade --install hinbert ./docker/kubernetes \
  --set image.repository=registry.example.com/hinbert-fastapi \
  --set image.tag=0.1.0 \
  --set secretKey="$SECRET_KEY"
```

The chart includes deployment, service, ConfigMap, Secret, optional ingress, non-root security context, dropped Linux capabilities, resource requests/limits, and `/health` liveness/readiness probes. Prefer external-secrets or a cloud secret operator for real credentials.

## CI/CD

`.github/workflows/ci.yml` installs development dependencies and runs Ruff, Black, and pytest with coverage. A release workflow should add image publishing, migration execution, Helm deployment, provenance signing, and environment approvals. Required CI secrets depend on the registry, cloud, SMTP, OAuth, and database provider.

## Migration Strategy

Run `alembic upgrade head` as a controlled pre-deploy job using the production `DATABASE_URL`. Use expand/migrate/contract changes for zero-downtime releases, back up before destructive changes, and never generate migrations automatically in the production process.

## Logging and Monitoring

Loguru writes JSON-serialized events to `logs/app.log` with 10 MB rotation and 30-day retention, plus standard output. Collect stdout and file logs centrally. Monitor HTTP 5xx/4xx rates, latency, rate-limit responses, database pool saturation, migration status, token failures, and health probes.

## Performance Tuning

Tune SQLAlchemy pool capacity to the PostgreSQL connection budget, use Redis-backed rate limiting for multiple replicas, keep pagination bounded, add indexes based on query plans, place TLS termination at a trusted ingress, and scale horizontally behind a load balancer. Avoid synchronous network calls inside async request handlers when throughput matters.

## Backup and Recovery

Use automated PostgreSQL point-in-time recovery and encrypted snapshots. Test restores regularly, document RPO/RTO, keep migration versions with releases, and verify that restored environments receive the correct secrets and application version.

## Security Checklist

- Use a secret manager and rotate `SECRET_KEY` with a planned token invalidation strategy.
- Restrict CORS to exact trusted origins.
- Use HTTPS and configure HSTS at the ingress.
- Protect OAuth redirect URIs and validate provider state/nonce in the surrounding identity integration.
- Encrypt database backups and TOTP secrets.
- Run migrations as a least-privileged deployment job.
- Set resource limits and non-root pod security.
- Keep dependencies patched and scan images.
- Disable debug behavior in production.
- Confirm logs contain no credentials or bearer tokens.
