from functools import wraps
from typing import Callable

from src.core.exceptions import RetriesAmountExceeded


# TODO сделать RetriableMixin


def retry_instancemethod(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(_instance, *args, **kwargs) -> Callable:
        @wraps(method)
        async def inner():
            for _ in range(_instance.max_retries):
                try:
                    result = await method(_instance, *args, **kwargs)
                    return result
                except Exception as e:
                    exception = e
                    # TODO Добавить логирование сюды
                    pass
            else:
                raise RetriesAmountExceeded(exception)

        return inner

    return wrapper
