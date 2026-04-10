from typing import Annotated
from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="Refresh token",
        ),
    ]


class TokensResponse(BaseModel):
    access_token: Annotated[
        str,
        Field(
            ...,
            description="Access token",
        ),
    ]

    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="Refresh token",
        ),
    ]

    token_type: Annotated[
        str,
        Field(
            default="Bearer",
            description="Token type (default=Bearer)",
        ),
    ]
