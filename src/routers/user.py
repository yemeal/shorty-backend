"""
Routes under /me (current user only).
"""
from uuid import UUID
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query, Body, HTTPException
from starlette import status

from src.models import User as UserModel
from src.schemas.pagination_meta import PaginationParams
from src.schemas.short_url import ShortUrl, ShortUrlListPage
from src.schemas.user import UserResponse
from src.schemas.user_profile import UserProfileUpdate, UserProfileResponse
from src.schemas import OkResponse
from src.utils.protocols import UserServiceProtocol, UserProfileServiceProtocol
from src.core.exceptions import DomainErrors, HTTPErrors

router = APIRouter(
    prefix="/me",
    tags=["account"],
)


@router.get(
    "/",
    response_model=UserResponse,
    summary="Current user",
    description="Needs a valid `access_token` cookie.",
)
@inject
async def get_me(
    current_user: FromDishka[UserModel],
):
    return current_user


@router.get(
    "/short_urls",
    response_model=ShortUrlListPage,
    summary="My short URLs",
    description="Paged list. Optional `q` searches slug and long URL. `sort_by` and `sort_order` control order.",
)
@inject
async def get_short_urls(
    user_service: FromDishka[UserServiceProtocol],
    current_user: FromDishka[UserModel],
    pagination_params: Annotated[PaginationParams, Query()],
):
    items, meta = await user_service.get_paginated_short_urls_by_user_id(
        current_user.id,
        pagination_params=pagination_params,
    )
    return ShortUrlListPage(
        items=[ShortUrl.model_validate(row) for row in items],
        meta=meta,
    )


@router.delete(
    "/short_urls/{short_url_id}",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse,
    summary="Delete short URL",
    description="Soft-deletes your short link by id (must belong to you).",
)
@inject
async def delete_short_url(
    short_url_id: UUID,
    user_service: FromDishka[UserServiceProtocol],
    current_user: FromDishka[UserModel],
):
    try:
        await user_service.delete_short_url_by_id(short_url_id, current_user.id)
    except DomainErrors.ShortUrl.ForOwnerNotFoundError:
        raise HTTPErrors.ShortUrl.SHORT_URL_NOT_FOUND()
    except Exception:
        raise HTTPErrors.Server.INTERNAL_ERROR()

    return {"ok": True}


@router.patch(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
    summary="Update profile",
    description="Update your profile.",
)
@inject
async def update_profile(
    user_profile_update: Annotated[UserProfileUpdate, Body()],
    user_profile_service: FromDishka[UserProfileServiceProtocol],
    current_user: FromDishka[UserModel],
):
    try:
        return await user_profile_service.update_user_profile(
            current_user.id, user_profile_update
        )
    except DomainErrors.UserProfile.NotFoundByUserIdError:
        raise HTTPErrors.User.USER_PROFILE_NOT_FOUND()