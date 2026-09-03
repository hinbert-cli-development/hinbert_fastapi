# Security Guide

## Authentication

Credential login verifies bcrypt hashes and returns a short-lived JWT access token plus an opaque refresh token. Access tokens contain a subject, type, issued-at time, and expiry. Invalid, expired, incorrectly typed, missing, or inactive-user tokens fail closed with HTTP 401.

## Password Security

Passwords are hashed with bcrypt and a random salt. Signup and reset schemas require 12-72 characters, matching bcrypt's 72-byte input limitation for ordinary ASCII credentials. Do not log passwords or accept credentials over unencrypted transport.

## JWT Configuration

`SECRET_KEY` must be at least 32 characters and cannot be the documented default. `ALGORITHM`, access lifetime, and refresh lifetime come from settings. Rotate the secret through an explicit session invalidation plan because changing it invalidates existing JWTs.

## Refresh Rotation

The raw refresh token is returned once; only its SHA-256 digest is stored. Refresh checks digest, expiry, revocation, and account state, revokes the predecessor, and creates a replacement. Logout marks the record revoked. This limits replay after normal rotation, but distributed deployments should also consider reuse detection and session-family revocation.

## Email Verification and Password Reset

Signup and reset workflows generate cryptographically random tokens, persist only SHA-256 digests, enforce expiry, and mark consumed rows. Forgot-password responses do not disclose whether an email exists. SMTP credentials must be supplied for real delivery.

## TOTP

TOTP setup creates a random secret and returns a standard provisioning URI. The database stores a Fernet-encrypted value derived from the application secret. Protect the secret during setup, require HTTPS, consider recovery codes, and never expose the stored ciphertext or key material.

## OAuth2

Google and Facebook routes redirect to providers and callbacks exchange authorization codes over HTTPS. Configure exact redirect URIs and client credentials. Production identity integrations should add state and nonce validation, PKCE where supported, provider audience/issuer validation, and account-linking policy before accepting external identities.

## Rate Limiting and CORS

SlowAPI decorators limit all API and health routes, with stricter limits on login, reset, and verification actions. The default limiter is process-local; configure shared Redis storage for multiple replicas. CORS uses the `BACKEND_CORS_ORIGINS` settings value and should contain exact trusted origins, never `*` with credentials.

## Secure Headers

The request middleware sets `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, and a restrictive `Permissions-Policy`. Configure `Strict-Transport-Security` at the HTTPS ingress after confirming every production path is TLS-only.

## SQL Injection Prevention

Repositories use SQLAlchemy expressions and bound parameters. Keep user-controlled sort values allowlisted, keep page sizes bounded, and never concatenate raw query strings into SQL.

## Environment Security

`.env` is ignored by Git. Use a secret manager in CI, containers, and Kubernetes. Rotate SMTP, OAuth, database, and JWT credentials, restrict file permissions, and ensure logs, crash dumps, images, and backups do not contain secret values.

## Production Checklist

- [ ] HTTPS enforced at ingress and HSTS configured.
- [ ] Strong secret-manager values supplied for every environment.
- [ ] Exact CORS origins configured.
- [ ] Redis-backed distributed rate limiting configured.
- [ ] OAuth state/nonce/PKCE and redirect URI policy reviewed.
- [ ] SMTP delivery tested without leaking tokens.
- [ ] TOTP backup/recovery policy implemented.
- [ ] Database user, network, backups, and migrations hardened.
- [ ] Container runs non-root with dropped capabilities and resource limits.
- [ ] Dependency and image vulnerability scans enabled.
- [ ] Observability alerts and incident response documented.
