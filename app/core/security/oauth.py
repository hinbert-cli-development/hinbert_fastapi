"""OAuth provider configuration boundary.

Provider exchange logic belongs in ``social_auth_service`` so credentials and
HTTP clients can be mocked in tests. Add provider-specific scopes and callback
URLs there without coupling the rest of the application to an SDK.
"""

SUPPORTED_PROVIDERS = ("google", "facebook")
