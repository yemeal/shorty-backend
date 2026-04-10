from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.schemas.tokens import RefreshTokenRequest, TokensResponse
from src.schemas.user import UserCreate
from src.schemas.auth import AuthResponse
from src.utils.protocols import AuthServiceProtocol
from src.core.exceptions import (
    UserWithEmailExistsException,
    UserWithUsernameExistsException,
    IncorrectEmailOrPasswordException,
    UserNotFoundException,
)
from src.core.exceptions import TokenException, TokenExpiredException

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
)
@inject
async def register(
    payload: Annotated[UserCreate, Body()],
    auth_service: FromDishka[AuthServiceProtocol],
):
    try:
        auth_response = await auth_service.register(
            str(payload.username),
            str(payload.email),
            str(payload.password),
        )
    except UserWithEmailExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    except UserWithUsernameExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )
    return auth_response


@router.post(
    "/login",
    response_model=TokensResponse,
)
@inject
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: FromDishka[AuthServiceProtocol],
):
    try:
        return await auth_service.login(
            # .username in form_data means email
            str(form_data.username),
            str(form_data.password),
        )
    except IncorrectEmailOrPasswordException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
@inject
async def logout():
    # TODO Invalidate refresh or clear cookies
    pass


@router.post(
    "/refresh",
    response_model=TokensResponse,
)
@inject
async def refresh(
    payload: Annotated[RefreshTokenRequest, Body()],
    auth_service: FromDishka[AuthServiceProtocol],
):
    try:
        tokens = await auth_service.refresh(payload.refresh_token)
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserNotFoundException:
        raise HTTPException(
            # TODO Точно ли стоит 404 возвращать
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token owner not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens
