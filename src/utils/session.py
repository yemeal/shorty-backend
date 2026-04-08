from typing import Protocol, Any


# Transaction protocol for UoW
class AsyncTransactionProtocol(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def close(self) -> None: ...


# Session protocol for repositories
class AsyncSessionProtocol(AsyncTransactionProtocol, Protocol):

    def add(self, instance: Any) -> None: ...

    async def delete(self, instance: Any) -> None: ...

    async def merge(self, instance: Any) -> Any: ...

    async def get(
            self, entity_class: type[Any], entity_id: Any
    ) -> Any | None: ...

    async def flush(self) -> None: ...

    async def execute(
            self, statement: Any, *args: Any, **kwargs: Any
    ) -> Any: ...
