from functools import wraps
from typing import Callable, Any

from src.core.exceptions import DomainErrors

# TODO сделать RetriableMixin


def retry_instancemethod(method: Callable) -> Callable:
    @wraps(method)
    async def wrapper(_instance: Any, *args: Any, **kwargs: Any) -> Any:
        exception = None
        for _ in range(_instance.max_retries):
            try:
                return await method(_instance, *args, **kwargs)
            except Exception as e:
                exception = e
                # TODO Добавить логирование сюды
                pass

        raise DomainErrors.Retry.BUDGET_EXCEEDED(
            operation=method.__name__,
            attempts=_instance.max_retries,
            last_error=exception,
        )

    return wrapper
