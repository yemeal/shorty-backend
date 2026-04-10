# region Short URL exceptions
class SlugException(Exception):
    pass


class SlugAlreadyExistsException(SlugException):
    pass


class ShortUrlGenerationException(SlugException):
    pass


class LongUrlNotFoundException(SlugException):
    pass


# endregion Short URL exceptions


# region Retry exceptions
class RetryException(Exception):
    pass


class RetriesAmountExceeded(RetryException):
    pass


# endregion Retry exceptions


# region User exceptions
class UserException(Exception):
    pass


class IncorrectEmailOrPasswordException(UserException):
    pass


class UserExistsException(UserException):
    pass


class UserWithEmailExistsException(UserExistsException):
    pass


class UserWithUsernameExistsException(UserExistsException):
    pass


class UserNotFoundException(UserException):
    pass


class UserWithEmailNotFoundException(UserNotFoundException):
    pass


class UserWithIdNotFoundException(UserNotFoundException):
    pass


class UserWithUsernameNotFoundException(UserNotFoundException):
    pass


# endregion User exceptions


# region Token/Auth exceptions
class TokenException(Exception):
    pass


class InvalidTokenException(TokenException):
    pass


class TokenExpiredException(InvalidTokenException):
    pass


class InvalidTokenTypeException(InvalidTokenException):
    pass


class TokenNoSubException(InvalidTokenException):
    pass


# endregion Token/Auth exceptions


class RepositoryException(Exception):
    pass


class CreatingException(RepositoryException):
    pass
