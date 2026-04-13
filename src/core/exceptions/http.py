from __future__ import annotations

"""
Centralized HTTPException factories.

Why:
- Keep endpoint/business logic focused on intent, not repetitive HTTPException boilerplate.
- Ensure consistent status codes and `detail` messages across the API.

Preferred call style (single entrypoint):
- `raise HTTPErrors.Auth.NOT_AUTHENTICATED()`
- `raise HTTPErrors.User.EMAIL_EXISTS()` — registration conflicts
- `raise HTTPErrors.ShortUrl.SLUG_ALREADY_EXISTS()` — short URL errors
- `raise HTTPErrors.ShortUrl.SHORT_URL_NOT_FOUND()` — owned short URL missing
- `raise HTTPErrors.Server.INTERNAL_ERROR()`, `HTTPErrors.Request.VALIDATION_ERROR()`, `HTTPErrors.RateLimit.TOO_MANY_REQUESTS()`

`HTTPErrors` groups nested error classes (`Auth`, `User`, `ShortUrl`, …).

Factories overview (status / message / when to use):

| Method / function               | Status | message (human)                     | When to use |
|---------------------------------|--------|-------------------------------------|-------------|
| NOT_AUTHENTICATED               | 401    | Not authenticated                   | Missing access/refresh cookie, no valid auth context |
| INCORRECT_EMAIL_OR_PASSWORD     | 401    | Incorrect email or password         | Login failure; do not reveal whether email exists |
| TOKEN_EXPIRED                   | 401    | Token expired                       | JWT `exp` reached |
| INVALID_TOKEN_TYPE              | 401    | Invalid token type                  | JWT `token_type` mismatch (access vs refresh) |
| TOKEN_SUBJECT_MISSING           | 401    | Token subject (sub) is missing      | JWT has no `sub` claim |
| COULD_NOT_VALIDATE_CREDENTIALS  | 401    | Could not validate credentials      | Invalid JWT/signature/format (generic) |
| USER_NOT_FOUND                  | 401    | User not found                      | Token is valid but referenced user does not exist |
| EMAIL_EXISTS                    | 409    | User with this email already exists | Register conflict (unique email) |
| USERNAME_EXISTS                 | 409    | User with this username already exists | Register conflict (unique username) |
| SLUG_ALREADY_EXISTS             | 409    | This short url already exists.      | Short URL slug conflict |
| ORIGINAL_URL_NOT_FOUND          | 404    | Original URL not found              | Redirect slug not found |
| SHORT_URL_NOT_FOUND             | 404    | Short URL not found                 | Authenticated delete/list row missing for owner |
| RETRIES_AMOUNT_EXCEEDED         | 500    | We had problem generating short url, try again later. | Retry budget exceeded |
| INTERNAL_ERROR                  | 500    | Internal server error               | Unexpected server-side failure |
| FORBIDDEN                       | 403    | Forbidden                           | Authenticated but not allowed (RBAC/ownership) |
| VALIDATION_ERROR                | 422    | Validation error                    | Semantically invalid request (custom validation) |
| TOO_MANY_REQUESTS               | 429    | Too many requests                   | Rate limiting / brute force mitigation |

Note:
- For cookie-auth flows, 401 responses include `WWW-Authenticate: Bearer` to match OAuth2 tooling.

Error codes:
- Each error has a stable `ApiErrorCode` in `detail`: `{ "code": <str>, "message": <str> }`.
- Frontend: match on `detail.code`, not on `message` alone.

TODO: consider stable internal `DomainErrorCode` parallel to `ApiErrorCode` for logs/metrics
(see package docstring in `domain.py`).
"""

from enum import Enum

from fastapi import HTTPException, status


class ApiErrorCode(str, Enum):
    """
    Stable, machine-readable error codes.

    Frontend tip: match on `detail.code` (not on human-readable messages).
    """

    NOT_AUTHENTICATED = "auth/not_authenticated"
    INCORRECT_EMAIL_OR_PASSWORD = "auth/incorrect_email_or_password"
    TOKEN_EXPIRED = "auth/token_expired"
    INVALID_TOKEN_TYPE = "auth/invalid_token_type"
    TOKEN_SUBJECT_MISSING = "auth/token_subject_missing"
    COULD_NOT_VALIDATE_CREDENTIALS = "auth/could_not_validate_credentials"
    USER_NOT_FOUND = "auth/user_not_found"

    USER_WITH_EMAIL_EXISTS = "user/email_exists"
    USER_WITH_USERNAME_EXISTS = "user/username_exists"

    SLUG_ALREADY_EXISTS = "short_url/slug_already_exists"
    ORIGINAL_URL_NOT_FOUND = "short_url/original_url_not_found"
    SHORT_URL_NOT_FOUND = "short_url/short_url_not_found"
    RETRIES_AMOUNT_EXCEEDED = "short_url/retries_amount_exceeded"

    INTERNAL_SERVER_ERROR = "server/internal_server_error"

    FORBIDDEN = "auth/forbidden"
    VALIDATION_ERROR = "request/validation_error"
    TOO_MANY_REQUESTS = "rate_limit/too_many_requests"


def _detail(code: ApiErrorCode, message: str) -> dict[str, str]:
    return {"code": code.value, "message": message}


_BEARER = {"WWW-Authenticate": "Bearer"}


class Auth:
    """Authentication and token-related HTTP errors (mostly 401)."""

    @staticmethod
    def NOT_AUTHENTICATED() -> HTTPException:
        """401: no valid auth context (e.g. missing access cookie)."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(ApiErrorCode.NOT_AUTHENTICATED, "Not authenticated"),
            headers=_BEARER,
        )

    @staticmethod
    def INCORRECT_EMAIL_OR_PASSWORD() -> HTTPException:
        """401: bad login; message stays vague on purpose."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(
                ApiErrorCode.INCORRECT_EMAIL_OR_PASSWORD,
                "Incorrect email or password",
            ),
            headers=_BEARER,
        )

    @staticmethod
    def TOKEN_EXPIRED() -> HTTPException:
        """401: JWT past `exp`."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(ApiErrorCode.TOKEN_EXPIRED, "Token expired"),
            headers=_BEARER,
        )

    @staticmethod
    def INVALID_TOKEN_TYPE() -> HTTPException:
        """401: JWT `token_type` does not match expected (access vs refresh)."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(ApiErrorCode.INVALID_TOKEN_TYPE, "Invalid token type"),
            headers=_BEARER,
        )

    @staticmethod
    def TOKEN_SUBJECT_MISSING() -> HTTPException:
        """401: JWT has no `sub` claim."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(
                ApiErrorCode.TOKEN_SUBJECT_MISSING,
                "Token subject (sub) is missing",
            ),
            headers=_BEARER,
        )

    @staticmethod
    def COULD_NOT_VALIDATE_CREDENTIALS() -> HTTPException:
        """401: invalid or unreadable JWT (generic)."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(
                ApiErrorCode.COULD_NOT_VALIDATE_CREDENTIALS,
                "Could not validate credentials",
            ),
            headers=_BEARER,
        )

    @staticmethod
    def USER_NOT_FOUND() -> HTTPException:
        """401: token OK but user id from `sub` does not resolve."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_detail(ApiErrorCode.USER_NOT_FOUND, "User not found"),
            headers=_BEARER,
        )

    @staticmethod
    def FORBIDDEN() -> HTTPException:
        """403: authenticated but not allowed (RBAC / resource ownership)."""
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_detail(ApiErrorCode.FORBIDDEN, "Forbidden"),
        )


class User:
    """User registration / uniqueness conflicts (not the ORM model)."""

    @staticmethod
    def EMAIL_EXISTS() -> HTTPException:
        """409: email already registered."""
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_detail(
                ApiErrorCode.USER_WITH_EMAIL_EXISTS,
                "User with this email already exists",
            ),
        )

    @staticmethod
    def USERNAME_EXISTS() -> HTTPException:
        """409: username already taken."""
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_detail(
                ApiErrorCode.USER_WITH_USERNAME_EXISTS,
                "User with this username already exists",
            ),
        )


class ShortUrl:
    """Short URL creation and redirect errors."""

    @staticmethod
    def SLUG_ALREADY_EXISTS() -> HTTPException:
        """409: slug collision."""
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_detail(
                ApiErrorCode.SLUG_ALREADY_EXISTS,
                "This short url already exists.",
            ),
        )

    @staticmethod
    def ORIGINAL_URL_NOT_FOUND() -> HTTPException:
        """404: unknown slug for redirect."""
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_detail(
                ApiErrorCode.ORIGINAL_URL_NOT_FOUND,
                "Original URL not found",
            ),
        )

    @staticmethod
    def SHORT_URL_NOT_FOUND() -> HTTPException:
        """404: short URL row missing for the current user (e.g. delete by id)."""
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_detail(
                ApiErrorCode.SHORT_URL_NOT_FOUND,
                "Short URL not found",
            ),
        )

    @staticmethod
    def RETRIES_AMOUNT_EXCEEDED() -> HTTPException:
        """500: slug generation retries exhausted."""
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_detail(
                ApiErrorCode.RETRIES_AMOUNT_EXCEEDED,
                "We had problem generating short url, try again later.",
            ),
        )


class Server:
    """Generic server failures."""

    @staticmethod
    def INTERNAL_ERROR() -> HTTPException:
        """500: unexpected failure; avoid leaking internals in message."""
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_detail(
                ApiErrorCode.INTERNAL_SERVER_ERROR,
                "Internal server error",
            ),
        )


class Request:
    """Request shape / semantic validation (beyond Pydantic)."""

    @staticmethod
    def VALIDATION_ERROR() -> HTTPException:
        """422: syntactically valid but semantically wrong."""
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_detail(ApiErrorCode.VALIDATION_ERROR, "Validation error"),
        )


class RateLimit:
    """Throttling and abuse protection."""

    @staticmethod
    def TOO_MANY_REQUESTS() -> HTTPException:
        """429: rate limit or brute-force backoff."""
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_detail(ApiErrorCode.TOO_MANY_REQUESTS, "Too many requests"),
        )


class HTTPErrors:
    """
    Namespace for HTTP error factories.

    Use `HTTPErrors.Auth.NOT_AUTHENTICATED()`, `HTTPErrors.User.EMAIL_EXISTS()`, etc.
    Nested attributes are the same classes as module-level `Auth`, `User`, …
    """

    Auth = Auth
    User = User
    ShortUrl = ShortUrl
    Server = Server
    Request = Request
    RateLimit = RateLimit
