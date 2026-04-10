from pydantic import BaseModel, Field
from typing import Annotated
from src.schemas.user import UserResponse
from src.schemas.tokens import TokensResponse


class AuthResponse(BaseModel):
    user: Annotated[
        UserResponse,
        Field(
            ...,
            description="User schema",
        ),
    ]
    tokens: Annotated[
        TokensResponse,
        Field(
            ...,
            description="Tokens (access+refresh) schema",
        ),
    ]

class AuthCookieResponse(BaseModel):
    user: Annotated[
        UserResponse,
        Field(
            ...,
            description="User schema",
        ),
    ]


class OkResponse(BaseModel):
    ok: Annotated[
        bool,
        Field(
            ...,
            description="Operation status"    
        )
    ]