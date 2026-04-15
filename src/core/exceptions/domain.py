from __future__ import annotations

"""
Domain-layer failures (never sent to the HTTP client as-is).

- Services and infra raise these when something breaks in business rules or persistence.
- Routers map them to :class:`HTTPErrors` before the response leaves the app.

Examples (same style as ``HTTPErrors`` where it helps):
- ``raise DomainErrors.Auth.INCORRECT_EMAIL_OR_PASSWORD()``
- ``raise DomainErrors.Token.EXPIRED(cause=exc)``
- ``raise DomainErrors.User.NOT_FOUND_BY_ID(user_id=uid)``
- ``raise DomainErrors.ShortUrl.SLUG_TAKEN(slug="foo")``
- ``raise DomainErrors.Persistence.INTEGRITY_VIOLATION(operation="insert", model="User")``

Groups:
- **Auth** - login checks (wrong password, etc.), not low-level JWT code.
- **Token** - read and check JWT (issuer, exp, claims).
- **User** - find user, clashes on unique email/username.
- **ShortUrl** - slug, redirect, saving a URL row.
- **Persistence** - DB layer (e.g. IntegrityError).
- **Retry** - a retry loop gave up (caller passes the operation name).
- **Authorization** - reserved for later (403 / who may do what).

Each error has:
- ``message`` - text for humans and logs.
- ``context`` - small dict safe enough for JSON logs (UUIDs as strings, nested errors shortened).
- ``note`` (optional) - extra hint for developers, not for end users.

Helpers:
- ``exc.describe()`` - one short line for logs.
- ``exc.context`` - the dict above.

TODO: optional ``DomainErrorCode`` enum next to ``ApiErrorCode`` for logging or tracing.
"""

from typing import Any
from uuid import UUID


def _normalize_context_value(value: Any) -> Any:
    """Make context values safe to log or JSON-encode where possible."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, BaseException):
        return {
            "type": type(value).__name__,
            "message": str(value),
        }
    if isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


class DomainError(Exception):
    """
    Base class for all domain failures.

    **Never** send this (or subclasses) straight to the client. Map to ``HTTPErrors`` in routers.
    """

    default_message: str = "Domain error"

    def __init__(
        self,
        message: str | None = None,
        *,
        note: str | None = None,
        cause: BaseException | None = None,
        **context: Any,
    ) -> None:
        self._note = note
        self.context: dict[str, Any] = {
            k: _normalize_context_value(v) for k, v in context.items() if v is not None
        }
        final_message = message or self.default_message
        super().__init__(final_message)
        if cause is not None:
            self.__cause__ = cause

    @property
    def note(self) -> str | None:
        """Optional developer-only annotation (logging, not for clients)."""
        return self._note

    def describe(self) -> str:
        """Compact description for log lines."""
        parts = [type(self).__name__, f"message={self.args[0]!r}"]
        if self.context:
            parts.append(f"context={self.context!r}")
        if self._note:
            parts.append(f"note={self._note!r}")
        return " ".join(parts)


# region Auth (credentials)


class AuthIncorrectCredentialsError(DomainError):
    """Login failed; do not use this to distinguish missing user vs bad password."""

    default_message = "Incorrect email or password"


# endregion


# region Token (JWT)


class TokenError(DomainError):
    """Base for JWT decode/validation failures in the token service."""


class TokenExpiredError(TokenError):
    default_message = "Token has expired"


class TokenInvalidTypeError(TokenError):
    default_message = "Token type does not match the expected value"


class TokenMissingSubjectError(TokenError):
    default_message = "Token payload has no subject (sub)"


class TokenMalformedError(TokenError):
    """Unreadable JWT (signature, format, algorithm, etc.)."""

    default_message = "Could not decode or validate token"


# endregion


# region User aggregate


class UserLookupError(DomainError):
    """Base: active user not found for a concrete lookup key."""


class UserNotFoundByEmailError(UserLookupError):
    default_message = "No active user with this email"


class UserNotFoundByIdError(UserLookupError):
    default_message = "No active user with this id"


class UserNotFoundByUsernameError(UserLookupError):
    default_message = "No active user with this username"


class UserConflictError(DomainError):
    """Base: uniqueness / business rule blocks user creation or update."""


class UserEmailAlreadyExistsError(UserConflictError):
    default_message = "User with this email already exists"


class UserUsernameAlreadyExistsError(UserConflictError):
    default_message = "User with this username already exists"


class UserInactiveError(DomainError):
    """Reserved: account disabled or soft-deleted user used where active is required."""

    default_message = "User account is inactive"


class UserEmailNotVerifiedError(DomainError):
    """Reserved: flows that will require verified email before proceeding."""

    default_message = "Email address is not verified"


# endregion


# region Short URL


class ShortUrlSlugConflictError(DomainError):
    """
    Base: requested slug cannot be used (collision with existing row or reserved name).

    Catch this in routers when a single HTTP status covers multiple slug rejection reasons.
    """


class ShortUrlSlugTakenError(ShortUrlSlugConflictError):
    default_message = "Slug is already in use"


class ShortUrlSlugReservedError(ShortUrlSlugConflictError):
    default_message = "Slug is reserved by the system"


class ShortUrlBySlugNotFoundError(DomainError):
    """No active short URL row for the given slug (public redirect)."""

    default_message = "No short URL found for slug"


class ShortUrlForOwnerNotFoundError(DomainError):
    """No active short URL for this id and owner (for example delete by id for the logged-in user)."""

    default_message = "Short URL not found for this user"


class ShortUrlGenerationFailedError(DomainError):
    """Persisting a new short URL failed for an unexpected reason."""

    default_message = "Failed to persist short URL"


class ShortUrlAccessDeniedError(DomainError):
    """Reserved: authenticated user cannot act on another user's short URL."""

    default_message = "Not allowed to access this short URL"


# endregion


# region Persistence / repository


class PersistenceIntegrityViolationError(DomainError):
    """DB reported a constraint violation (e.g. unique) during a write."""

    default_message = "Database integrity constraint violated"


class PersistenceStaleStateError(DomainError):
    """Reserved: optimistic locking / version mismatch on update."""

    default_message = "Entity was modified by another operation"


# endregion


# region Retry policy


class RetryBudgetExceededError(DomainError):
    """Caller exhausted configured retry attempts."""

    default_message = "Maximum retry attempts exceeded"


# endregion


# region Authorization (future RBAC)


class AuthorizationForbiddenError(DomainError):
    """Reserved: authenticated but lacking permission for the resource/action."""

    default_message = "Operation forbidden for current principal"


# endregion


# region Session / refresh tokens (future)


class SessionRefreshRevokedError(DomainError):
    """Reserved: refresh token invalidated server-side."""

    default_message = "Refresh token has been revoked"


# endregion

# region User Profile


class UserProfileLookupError(DomainError):
    """Base: user profile not found for a concrete lookup key."""


class UserProfileNotFoundByUserIdError(UserProfileLookupError):
    """No profile row for this user id."""

    default_message = "No user profile with this user id"


# endregion


class UserProfile:
    """Profile row lookups (not found, etc.)."""

    LookupError = UserProfileLookupError
    NotFoundByUserIdError = UserProfileNotFoundByUserIdError

    @staticmethod
    def NOT_FOUND_BY_USER_ID(*, user_id: UUID, note: str | None = None) -> UserProfileNotFoundByUserIdError:
        return UserProfileNotFoundByUserIdError(note=note, user_id=user_id)


class Auth:
    """Credential verification (login), not JWT parsing."""

    IncorrectCredentialsError = AuthIncorrectCredentialsError

    @staticmethod
    def INCORRECT_EMAIL_OR_PASSWORD(
        *,
        note: str | None = None,
    ) -> AuthIncorrectCredentialsError:
        return AuthIncorrectCredentialsError(note=note)


class Token:
    """JWT decode and claim validation."""

    Error = TokenError
    ExpiredError = TokenExpiredError
    InvalidTypeError = TokenInvalidTypeError
    MissingSubjectError = TokenMissingSubjectError
    MalformedError = TokenMalformedError

    @staticmethod
    def EXPIRED(*, cause: BaseException | None = None, note: str | None = None) -> TokenExpiredError:
        return TokenExpiredError(note=note, cause=cause)

    @staticmethod
    def INVALID_TYPE(
        *,
        expected: str | None = None,
        actual: str | None = None,
        note: str | None = None,
    ) -> TokenInvalidTypeError:
        return TokenInvalidTypeError(note=note, expected=expected, actual=actual)

    @staticmethod
    def SUBJECT_MISSING(*, note: str | None = None) -> TokenMissingSubjectError:
        return TokenMissingSubjectError(note=note)

    @staticmethod
    def MALFORMED(*, cause: BaseException | None = None, note: str | None = None) -> TokenMalformedError:
        return TokenMalformedError(note=note, cause=cause)


class User:
    """User lookups and registration conflicts."""

    LookupError = UserLookupError
    NotFoundByEmailError = UserNotFoundByEmailError
    NotFoundByIdError = UserNotFoundByIdError
    NotFoundByUsernameError = UserNotFoundByUsernameError
    ConflictError = UserConflictError
    EmailAlreadyExistsError = UserEmailAlreadyExistsError
    UsernameAlreadyExistsError = UserUsernameAlreadyExistsError
    InactiveError = UserInactiveError
    EmailNotVerifiedError = UserEmailNotVerifiedError

    @staticmethod
    def NOT_FOUND_BY_EMAIL(*, email: str, note: str | None = None) -> UserNotFoundByEmailError:
        return UserNotFoundByEmailError(note=note, email=email)

    @staticmethod
    def NOT_FOUND_BY_ID(*, user_id: UUID, note: str | None = None) -> UserNotFoundByIdError:
        return UserNotFoundByIdError(note=note, user_id=user_id)

    @staticmethod
    def NOT_FOUND_BY_USERNAME(*, username: str, note: str | None = None) -> UserNotFoundByUsernameError:
        return UserNotFoundByUsernameError(note=note, username=username)

    @staticmethod
    def EMAIL_ALREADY_EXISTS(*, email: str | None = None, note: str | None = None) -> UserEmailAlreadyExistsError:
        return UserEmailAlreadyExistsError(note=note, email=email)

    @staticmethod
    def USERNAME_ALREADY_EXISTS(
        *,
        username: str | None = None,
        note: str | None = None,
    ) -> UserUsernameAlreadyExistsError:
        return UserUsernameAlreadyExistsError(note=note, username=username)

    @staticmethod
    def INACTIVE(*, user_id: UUID | None = None, note: str | None = None) -> UserInactiveError:
        return UserInactiveError(note=note, user_id=user_id)

    @staticmethod
    def EMAIL_NOT_VERIFIED(*, email: str | None = None, note: str | None = None) -> UserEmailNotVerifiedError:
        return UserEmailNotVerifiedError(note=note, email=email)


class ShortUrl:
    """Short URL creation, validation, redirect, and owner-scoped operations."""

    SlugConflictError = ShortUrlSlugConflictError
    SlugTakenError = ShortUrlSlugTakenError
    SlugReservedError = ShortUrlSlugReservedError
    BySlugNotFoundError = ShortUrlBySlugNotFoundError
    ForOwnerNotFoundError = ShortUrlForOwnerNotFoundError
    GenerationFailedError = ShortUrlGenerationFailedError
    AccessDeniedError = ShortUrlAccessDeniedError

    @staticmethod
    def SLUG_TAKEN(
        *,
        slug: str,
        message: str | None = None,
        note: str | None = None,
    ) -> ShortUrlSlugTakenError:
        if message is not None:
            return ShortUrlSlugTakenError(message, note=note, slug=slug)
        return ShortUrlSlugTakenError(note=note, slug=slug)

    @staticmethod
    def SLUG_RESERVED(*, slug: str, note: str | None = None) -> ShortUrlSlugReservedError:
        return ShortUrlSlugReservedError(note=note, slug=slug)

    @staticmethod
    def BY_SLUG_NOT_FOUND(*, slug: str, note: str | None = None) -> ShortUrlBySlugNotFoundError:
        return ShortUrlBySlugNotFoundError(note=note, slug=slug)

    @staticmethod
    def NOT_FOUND_FOR_OWNER(
        *,
        short_url_id: UUID,
        user_id: UUID,
        note: str | None = None,
    ) -> ShortUrlForOwnerNotFoundError:
        return ShortUrlForOwnerNotFoundError(
            note=note,
            short_url_id=short_url_id,
            user_id=user_id,
        )

    @staticmethod
    def GENERATION_FAILED(
        *,
        cause: BaseException | None = None,
        slug: str | None = None,
        note: str | None = None,
    ) -> ShortUrlGenerationFailedError:
        return ShortUrlGenerationFailedError(note=note, cause=cause, slug=slug)

    @staticmethod
    def ACCESS_DENIED(
        *,
        short_url_id: UUID | None = None,
        user_id: UUID | None = None,
        note: str | None = None,
    ) -> ShortUrlAccessDeniedError:
        return ShortUrlAccessDeniedError(
            note=note,
            short_url_id=short_url_id,
            user_id=user_id,
        )


class Persistence:
    """Repository and database semantics that are not specific to one aggregate."""

    IntegrityViolationError = PersistenceIntegrityViolationError
    StaleStateError = PersistenceStaleStateError

    @staticmethod
    def INTEGRITY_VIOLATION(
        *,
        operation: str | None = None,
        model: str | None = None,
        cause: BaseException | None = None,
        note: str | None = None,
    ) -> PersistenceIntegrityViolationError:
        return PersistenceIntegrityViolationError(
            note=note,
            cause=cause,
            operation=operation,
            model=model,
        )

    @staticmethod
    def STALE_STATE(
        *,
        entity: str | None = None,
        entity_id: UUID | None = None,
        note: str | None = None,
    ) -> PersistenceStaleStateError:
        return PersistenceStaleStateError(note=note, entity=entity, entity_id=entity_id)


class Retry:
    """Retry helper / policy exhaustion."""

    BudgetExceededError = RetryBudgetExceededError

    @staticmethod
    def BUDGET_EXCEEDED(
        *,
        operation: str | None = None,
        attempts: int | None = None,
        last_error: BaseException | None = None,
        note: str | None = None,
    ) -> RetryBudgetExceededError:
        return RetryBudgetExceededError(
            note=note,
            cause=last_error,
            operation=operation,
            attempts=attempts,
        )


class Authorization:
    """Future: map to ``HTTPErrors.Auth.FORBIDDEN()`` at the router."""

    ForbiddenError = AuthorizationForbiddenError

    @staticmethod
    def FORBIDDEN(
        *,
        resource: str | None = None,
        action: str | None = None,
        note: str | None = None,
    ) -> AuthorizationForbiddenError:
        return AuthorizationForbiddenError(note=note, resource=resource, action=action)


class Session:
    """Future: refresh-token store and rotation rules."""

    RefreshRevokedError = SessionRefreshRevokedError

    @staticmethod
    def REFRESH_REVOKED(*, note: str | None = None) -> SessionRefreshRevokedError:
        return SessionRefreshRevokedError(note=note)


class DomainErrors:
    """
    Namespace for domain error factories and exception types.

    Use ``DomainErrors.User.NOT_FOUND_BY_ID(user_id=...)`` to raise; catch
    ``DomainErrors.User.NotFoundByIdError`` (or broader bases like ``UserLookupError``).
    """

    Auth = Auth
    Token = Token
    User = User
    UserProfile = UserProfile
    ShortUrl = ShortUrl
    Persistence = Persistence
    Retry = Retry
    Authorization = Authorization
    Session = Session
