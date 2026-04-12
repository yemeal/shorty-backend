"""
User-scoped routes (/me).
"""

from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query

from src.models import User as UserModel
from src.schemas.pagination_meta import PaginationParams
from src.schemas.short_url import ShortUrl, ShortUrlListPage
from src.schemas.user import UserResponse
from src.utils.protocols import UserServiceProtocol

router = APIRouter(
    prefix="/me",
    tags=["account"],
)


@router.get(
    "/",
    response_model=UserResponse,
    summary="Current user",
    description="Requires `access_token` cookie.",
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
    description="Paginated list with optional `q` search and `sort_by` / `sort_order`.",
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
