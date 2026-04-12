"""OpenAPI title, description, and tag ordering for Swagger / Redoc."""

API_TITLE = "Shorty API"
API_DESCRIPTION = (
    "URL shortener: create links, list your links, resolve slugs. "
    "Auth uses **httpOnly** cookies (`access_token`, `refresh_token`); "
    "send requests with `credentials: include` from the browser."
)

OPENAPI_TAGS = [
    {
        "name": "auth",
        "description": "Register, login, refresh, logout. Sets and clears token cookies.",
    },
    {
        "name": "account",
        "description": "Current user profile and owned short URLs. Requires `access_token` cookie.",
    },
    {
        "name": "short-urls",
        "description": "Create a short link. Optional login attaches the link to your account.",
    },
    {
        "name": "redirect",
        "description": "Public: open `/{slug}` to follow a short link (HTTP 302).",
    },
]
