from typing import Any, Protocol

from src.models import User

class TokenServiceProtocol(Protocol):
    def create_token(
        self,
        payload: dict[str, Any],
        token_type: str,
    ) -> str: ...

    def decode_token(
        self,
        token: str,
        token_type: str,
    ) -> dict[str, Any]: ...

    def issue_token(
        self,
        user: User,
        token_type: str,
    ) -> str: ...
