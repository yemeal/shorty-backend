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

# endregion User exceptions


# region Token/Auth exceptions
class TokenException(Exception):
    pass


class TokenExpiredException(TokenException):
    pass


class InvalidTokenTypeException(TokenException):
    pass


class TokenNoSubException(TokenException):
    pass
# endregion Token/Auth exceptions