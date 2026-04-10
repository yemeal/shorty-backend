from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from uuid import UUID


class UserCreate(BaseModel):
    username: Annotated[
        str,
        Field(
            ...,
            description="Username (max 20 characters)",
            max_length=20,
        ),
    ]
    password: Annotated[
        str,
        Field(
            ...,
            description="Password of the user (8-100 symbols)",
            min_length=8,
            max_length=100,
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description="Email address of the user (max 255 characters long)",
            max_length=255,
        ),
    ]


class UserResponse(BaseModel):
    id: Annotated[
        UUID,
        Field(..., description="Unique identifier of the user"),
    ]

    username: Annotated[
        str,
        Field(..., description="Username"),
    ]
    email: Annotated[
        str | None,
        Field(
            default=None,
            description="Email address of the user",
        ),
    ]

    is_active: Annotated[
        bool,
        Field(
            ...,
            description="Whether the user is active",
        ),
    ]

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    pass
