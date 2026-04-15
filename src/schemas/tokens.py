from typing import Annotated
from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="Refresh JWT in the body (cookie flow may not use this)",
        ),
    ]


class TokensResponse(BaseModel):
    access_token: Annotated[
        str,
        Field(
            ...,
            description="Short-lived access JWT",
        ),
    ]

    refresh_token: Annotated[
        str,
        Field(
            ...,
            description="Long-lived refresh JWT",
        ),
    ]

    token_type: Annotated[
        str,
        Field(
            default="Bearer",
            description="Always Bearer for these tokens",
        ),
    ]
