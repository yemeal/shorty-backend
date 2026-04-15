from pydantic import BaseModel, Field
from typing import Annotated
from src.schemas.user import UserResponse
from src.schemas.tokens import TokensResponse


class AuthResponse(BaseModel):
    user: Annotated[
        UserResponse,
        Field(
            ...,
            description="Logged-in user with profile",
        ),
    ]
    tokens: Annotated[
        TokensResponse,
        Field(
            ...,
            description="Access and refresh tokens in JSON (if you use this shape)",
        ),
    ]


class AuthCookieResponse(BaseModel):
    user: Annotated[
        UserResponse,
        Field(
            ...,
            description="Logged-in user with profile (tokens are only in cookies, not here)",
        ),
    ]


class OkResponse(BaseModel):
    ok: Annotated[
        bool,
        Field(
            ...,
            description="True when the action finished without error",
        ),
    ]