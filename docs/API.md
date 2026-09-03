# API Reference

## Base URL and Authentication

The versioned base path is `/api/v1`. Local development uses `http://localhost:8000`. Protected requests send:

```http
Authorization: Bearer <access_token>
```

All JSON responses use:

```json
{"success": true, "message": "OK", "data": {}, "errors": [], "status_code": 200}
```

## Authentication

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/signup` | None | Create an account and send verification email |
| POST | `/auth/login` | None | Return access and refresh tokens |
| POST | `/auth/refresh` | None | Rotate a refresh token |
| POST | `/auth/logout` | None | Revoke a refresh token |
| POST | `/auth/verify-email` | None | Consume an email token |
| POST | `/auth/forgot-password` | None | Send a reset token without account disclosure |
| POST | `/auth/reset-password` | None | Consume reset token and change password |
| POST | `/auth/totp/setup` | Access | Create encrypted TOTP secret and URI |
| POST | `/auth/totp/verify` | Access | Verify a six-digit TOTP code |
| GET | `/auth/google` | None | Redirect to Google authorization |
| GET | `/auth/google/callback?code=...` | None | Exchange Google authorization code |
| GET | `/auth/facebook` | None | Redirect to Facebook authorization |
| GET | `/auth/facebook/callback?code=...` | None | Exchange Facebook authorization code |

### Signup

`POST /auth/signup`

```json
{"email":"user@example.com","full_name":"Example User","password":"StrongPassword!123"}
```

Password length is 12-72 characters. Response data is a user object without password material.

### Login, Refresh, Logout

Login accepts `email` and `password`; `data` contains `access_token`, `refresh_token`, and `token_type`. Refresh and logout accept:

```json
{"refresh_token":"opaque-token"}
```

Refresh rotates the token. The predecessor is invalid immediately after rotation.

### Verification and Recovery

Verification accepts `{"token":"..."}`. Forgot password accepts `{"email":"..."}` and intentionally returns the same message whether the account exists. Reset accepts `{"token":"...","password":"NewStrongPassword!123"}`.

### TOTP

`POST /auth/totp/setup` returns `secret` and `provisioning_uri`. Submit the current six-digit authenticator value to `/auth/totp/verify` as `{"code":"123456"}`.

## Users

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/auth/me` | Access | Return current user |
| PATCH | `/users/me` | Access | Update current `full_name` |
| GET | `/users` | Admin | Paginated user list |
| GET | `/users/{user_id}` | Admin | Retrieve one user |
| PATCH | `/users/{user_id}` | Admin | Update profile, active state, or admin role |
| DELETE | `/users/{user_id}` | Admin | Delete a user and dependent records |

Admin payloads may contain `full_name`, `is_active`, and `is_admin`.

There is intentionally no `GET /users/me` route in the current router; use `GET /auth/me` for the current-user representation and `PATCH /users/me` for profile updates.

## Products

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/products` | None | Paginated collection |
| POST | `/products` | Access | Create an owned product |
| GET | `/products/{product_id}` | None | Retrieve one product |
| PUT | `/products/{product_id}` | Owner/Admin | Replace editable product fields |
| DELETE | `/products/{product_id}` | Owner/Admin | Delete a product |

Product JSON uses `name`, `description`, `price`, and `category`. Collection query parameters are `page` (default 1), `page_size` (1-100, default 20), `category`, `min_price`, `max_price`, and `sort_by` (`name`, `price`, or `created_at`). The response data is `{items, total_count, page, limit}`.

## Dashboard and Health

- `GET /api/v1/dashboard/stats` requires admin access and returns `users`, `products`, and `active_sessions`.
- `GET /health` returns `{"status":"ok"}` and is intended for load-balancer probes.

## Errors

| Status | Meaning |
|---:|---|
| 400 | Invalid request, expired token, or invalid workflow token |
| 401 | Missing/invalid credentials or inactive account |
| 403 | Framework-level forbidden response where applicable |
| 404 | Resource does not exist |
| 409 | Uniqueness conflict from the database/application layer |
| 422 | Pydantic validation failure |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error; inspect structured logs |

Validation errors may use FastAPI's native validation format, while domain errors use the standard envelope.
