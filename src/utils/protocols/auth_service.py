from typing import Protocol
from src.models.user import User


class AuthServiceProtocol(Protocol):
    async def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> dict[str, User | dict[str, str]]:
        """
        returns: dict("user": <user>, "tokens": <tokens (access and refresh)>)
        """
        ...

    async def login(
        self,
        email: str,
        password: str,
    ) -> dict[str, str]: ...

    async def refresh(
        self,
        refresh_token: str,
    ) -> dict[str, str]: ...

    async def logout(
        self,
        refresh_token: str | None = None,
    ): ...
