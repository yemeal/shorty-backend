from datetime import datetime, timedelta, timezone
from typing import Any, Final

import jwt

from src.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    ALGORITHM,
)
from src.core.exceptions import (
    InvalidTokenTypeException,
    TokenExpiredException,
    TokenNoSubException,
    TokenException,
)
from src.models import User


class JWTTokenService:
    _ALLOWED_TOKEN_TYPES: Final[set[str]] = {"access", "refresh"}

    def _check_token_type(self, token_type: str) -> None:
        if token_type not in self._ALLOWED_TOKEN_TYPES:
            raise InvalidTokenTypeException()

    def create_token(self, data: dict, token_type: str):
        self._check_token_type(token_type)

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=(
                ACCESS_TOKEN_EXPIRE_MINUTES
                if token_type == "access"
                else 0
            ),
            days=(
                REFRESH_TOKEN_EXPIRE_DAYS if token_type == "refresh" else 0
            ),
        )
        to_encode.update(
            {
                "exp": expire,
                "token_type": token_type,
            }
        )
        return jwt.encode(
            payload=to_encode,
            key=SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def decode_token(self, token: str, token_type: str) -> dict[str, Any]:
        self._check_token_type(token_type)

        try:
            payload = jwt.decode(
                token,
                key=SECRET_KEY,
                algorithms=[ALGORITHM],
            )
            if payload.get("sub") is None:
                raise TokenNoSubException()
            if payload.get("token_type") != token_type:
                raise InvalidTokenTypeException()
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.PyJWTError:
            raise TokenException()

        return payload

    def issue_token(self, user: User, token_type: str) -> str:
        self._check_token_type(token_type)

        token = self.create_token({"sub": str(user.id)}, token_type)
        return token
