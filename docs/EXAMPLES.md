# Examples

All examples assume the server is running at `http://localhost:8000` and the local database has been migrated.

## Basic API

```bash
uvicorn app.main:app --reload
curl http://localhost:8000/health
```

## Signup, Login, Refresh, Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","full_name":"Example User","password":"StrongPassword!123"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"StrongPassword!123"}'

curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"<refresh-token>"}'

curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"<rotated-refresh-token>"}'
```

Refresh tokens are one-time rotated. Replace placeholders with values from the preceding response.

## Product CRUD

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <access-token>" -H 'Content-Type: application/json' \
  -d '{"name":"Widget","description":"Useful widget","price":"12.50","category":"tools"}'

curl http://localhost:8000/api/v1/products/<product-id>
curl -X PUT http://localhost:8000/api/v1/products/<product-id> \
  -H "Authorization: Bearer <access-token>" -H 'Content-Type: application/json' \
  -d '{"name":"Better Widget","description":"Updated","price":"15.00","category":"tools"}'
curl -X DELETE http://localhost:8000/api/v1/products/<product-id> -H "Authorization: Bearer <access-token>"
```

## Pagination, Filtering, Sorting

```text
GET /api/v1/products?page=2&page_size=20&category=tools&min_price=10&max_price=100&sort_by=price
```

The response includes `items`, `total_count`, `page`, and `limit`. Valid sort fields are `name`, `price`, and `created_at`.

## Email Verification

Signup sends a token through configured SMTP. The client posts the received token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/verify-email \
  -H 'Content-Type: application/json' -d '{"token":"<verification-token>"}'
```

For local tests, monkeypatch `send_verification_email` or use an SMTP capture service; do not print real tokens in production logs.

## Password Reset

```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H 'Content-Type: application/json' -d '{"email":"user@example.com"}'

curl -X POST http://localhost:8000/api/v1/auth/reset-password \
  -H 'Content-Type: application/json' \
  -d '{"token":"<reset-token>","password":"NewStrongPassword!123"}'
```

## TOTP

```bash
curl -X POST http://localhost:8000/api/v1/auth/totp/setup \
  -H "Authorization: Bearer <access-token>"

curl -X POST http://localhost:8000/api/v1/auth/totp/verify \
  -H "Authorization: Bearer <access-token>" -H 'Content-Type: application/json' \
  -d '{"code":"123456"}'
```

Add the returned `provisioning_uri` to an authenticator app. The code changes every time window, so the example code is illustrative only.

## OAuth

Open `/api/v1/auth/google` or `/api/v1/auth/facebook` in a browser. The provider redirects to the matching callback with `?code=...`; the callback exchanges it and returns the normal token response. Configure exact provider redirect URIs and credentials first.

## Admin Operations

Create an administrator with a hidden password prompt:

```bash
python scripts/create_admin.py --email admin@example.com --full-name "Platform Admin"
```

Use the returned admin account to call `/api/v1/users`, `/api/v1/users/{user_id}`, and `/api/v1/dashboard/stats`. Admin-only authorization is enforced by `get_current_admin`.

## Docker Deployment

```bash
Copy-Item .env.example .env
# Replace SECRET_KEY and production connection values.
docker compose -f docker/docker-compose.yml up -d --build
curl http://localhost:8000/health
```

For Kubernetes, configure `values.yaml` or pass Helm `--set` values, supply secrets through an external secret manager, and install with `helm upgrade --install` as described in `DEPLOYMENT.md`.
