from typing import Protocol
from src.models.user import User
from src.schemas.user import UserCreate


class AuthServiceProtocol(Protocol):
    async def register(
        self,
        user_create: UserCreate,
    ) -> dict[str, User]:
        """
        returns: dict("user": <user>)
        """
        ...

    async def login(
        self,
        email: str,
        password: str,
    ) -> dict[str, User]:
        """
        returns: dict("user": <user>)
        """
        ...

    async def refresh(
        self,
        refresh_token: str,
    ) -> dict[str, str]: ...

    async def logout(
        self,
        refresh_token: str | None = None,
    ): ...
