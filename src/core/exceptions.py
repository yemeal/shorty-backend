class SlugException(Exception):
    pass


class SlugAlreadyExistsException(SlugException):
    pass


class ShortUrlGenerationException(SlugException):
    pass


class LongUrlNotFoundException(SlugException):
    pass
