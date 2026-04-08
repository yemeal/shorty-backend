from abc import ABC, abstractmethod
from types import TracebackType

from src.utils import AsyncTransactionProtocol


# Abstract Asynchronous Unit of Work
class AbstractAsyncUOW(ABC):
    @abstractmethod
    async def __aenter__(self) -> "AbstractAsyncUOW":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError


# Concrete Asynchronous Unit of Work
class AsyncUOW[SessionType: AsyncTransactionProtocol](AbstractAsyncUOW):
    def __init__(
            self,
            session: SessionType,
            close_session_on_exit: bool = False,
    ) -> None:
        self.session = session
        self.close_session_on_exit = close_session_on_exit

    async def __aenter__(self) -> "AsyncUOW[SessionType]":
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:

        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()

        if self.close_session_on_exit:
            await self.session.close()
