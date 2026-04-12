from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.schemas.tokens import RefreshTokenRequest, TokensResponse
from src.schemas.user import UserCreate
from src.schemas.auth import AuthCookieResponse, OkResponse
from src.utils.protocols import AuthServiceProtocol
from src.core.exceptions import (
    UserWithEmailExistsException,
    UserWithUsernameExistsException,
    IncorrectEmailOrPasswordException,
    UserNotFoundException,
)
from src.core.exceptions import TokenException, TokenExpiredException
from src.core.http_exceptions import HTTPErrors
from src.core.config import COOKIE_DOMAIN, COOKIE_SAMESITE, COOKIE_SECURE, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def _set_tokens_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    # access cookie 
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,       
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    # refresh cookie 
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,       
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/auth",
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthCookieResponse,
    summary="Register",
    description="Create user and set access + refresh cookies.",
)
@inject
async def register(
    payload: Annotated[UserCreate, Body()],
    response: Response,
    auth_service: FromDishka[AuthServiceProtocol],
):
    try:
        auth_response = await auth_service.register(
            str(payload.username),
            str(payload.email),
            str(payload.password),
        )
    except UserWithEmailExistsException:
        raise HTTPErrors.User.EMAIL_EXISTS()
    except UserWithUsernameExistsException:
        raise HTTPErrors.User.USERNAME_EXISTS()

    _set_tokens_cookies(
        response,
        access_token=auth_response["tokens"]["access_token"],
        refresh_token=auth_response["tokens"]["refresh_token"]
    )

    return {
        "user": auth_response["user"],
    }




@router.post(
    "/login",
    response_model=AuthCookieResponse,
    summary="Login",
    description="OAuth2 form: `username` = email, `password`. Sets token cookies.",
)
@inject
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    auth_service: FromDishka[AuthServiceProtocol],
):
    try:
        auth_response = await auth_service.login(
            # .username in form_data means email
            str(form_data.username),
            str(form_data.password),
        )
    except IncorrectEmailOrPasswordException:
        raise HTTPErrors.Auth.INCORRECT_EMAIL_OR_PASSWORD()

    _set_tokens_cookies(
        response,
        access_token=auth_response["tokens"]["access_token"],
        refresh_token=auth_response["tokens"]["refresh_token"]
    )

    return {
        "user": auth_response["user"],
    }


@router.post(
    "/refresh",
    response_model=OkResponse,
    summary="Refresh tokens",
    description="Reads `refresh_token` cookie; rotates tokens.",
)
@inject
async def refresh(
    request: Request,
    response: Response,
    auth_service: FromDishka[AuthServiceProtocol],
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPErrors.Auth.NOT_AUTHENTICATED()

    try:
        tokens = await auth_service.refresh(refresh_token)
    except TokenExpiredException:
        raise HTTPErrors.Auth.TOKEN_EXPIRED()
    except TokenException:
        raise HTTPErrors.Auth.COULD_NOT_VALIDATE_CREDENTIALS()
    except UserNotFoundException:
        raise HTTPErrors.Auth.USER_NOT_FOUND()

    _set_tokens_cookies(
        response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {"ok": True}


@router.post(
    "/logout",
    response_model=OkResponse,
    summary="Logout",
    description="Clears access and refresh cookies (client-side session end).",
)
@inject
async def logout(
    response: Response,
):
    # TODO Invalidate refresh from db
    response.delete_cookie(
        "access_token", 
        path="/",
    )
    response.delete_cookie(
        "refresh_token",
        path="/auth",
    )

    return {"ok": True}
