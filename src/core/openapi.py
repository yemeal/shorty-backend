"""OpenAPI title, description, and tag list for Swagger / Redoc.

If you add a new ``ApiErrorCode`` in ``src/core/exceptions/http``, add the same
value to the table in ``API_DESCRIPTION`` so Swagger stays correct.
"""

API_TITLE = "Shorty API"
API_DESCRIPTION = (
    "Shorty is a URL shortener: create short links, list yours, open a slug and get redirected. "
    "Auth uses **httpOnly** cookies (`access_token`, `refresh_token`). "
    "From the browser, send requests with `credentials: include` so cookies go with each call.\n\n"
    "**Errors from our app (login, register, business rules):** "
    "`detail` is one JSON object: `code` (string) and `message` (string). "
    "In the client, branch on **`detail.code`**. "
    "Do not rely only on `message` - we may change the wording.\n\n"
    "**422 body validation (Pydantic):** `detail` is usually a **list** of field errors. "
    "That shape is not the same as the table below.\n\n"
    "| `detail.code` | HTTP (typical) |\n"
    "|---|---|\n"
    "| `auth/not_authenticated` | 401 |\n"
    "| `auth/incorrect_email_or_password` | 401 |\n"
    "| `auth/token_expired` | 401 |\n"
    "| `auth/invalid_token_type` | 401 |\n"
    "| `auth/token_subject_missing` | 401 |\n"
    "| `auth/could_not_validate_credentials` | 401 |\n"
    "| `auth/user_not_found` | 401 |\n"
    "| `auth/forbidden` | 403 |\n"
    "| `user/email_exists` | 409 |\n"
    "| `user/username_exists` | 409 |\n"
    "| `short_url/slug_already_exists` | 409 |\n"
    "| `short_url/original_url_not_found` | 404 |\n"
    "| `short_url/short_url_not_found` | 404 |\n"
    "| `short_url/retries_amount_exceeded` | 500 |\n"
    "| `server/internal_server_error` | 500 |\n"
    "| `request/validation_error` | 422 |\n"
    "| `rate_limit/too_many_requests` | 429 |\n"
)

OPENAPI_TAGS = [
    {
        "name": "auth",
        "description": "Sign up, log in, refresh session, log out. Writes or clears auth cookies.",
    },
    {
        "name": "account",
        "description": "Current user and your short links. Needs a valid `access_token` cookie.",
    },
    {
        "name": "short-urls",
        "description": "Create a short link. If you are logged in, the link is tied to your account.",
    },
    {
        "name": "redirect",
        "description": "Public: open `/{slug}` in the browser. Returns HTTP 302 to the long URL.",
    },
]
