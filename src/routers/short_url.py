from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body
from starlette import status

from src.core.exceptions import DomainErrors, HTTPErrors
from src.utils.protocols import UrlServiceProtocol
from src.models import User as UserModel
from src.schemas.short_url import (
    ShortUrlCreate,
    ShortUrlResponse,
)

router = APIRouter(
    prefix="/short_url",
    tags=["short-urls"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ShortUrlResponse,
    summary="Create short URL",
    description="Random slug if omitted; custom `slug` if provided. Authenticated users get `user_id` set.",
)
@inject
async def create_short_url(
    payload: Annotated[
        ShortUrlCreate,
        Body(),
    ],
    url_service: FromDishka[UrlServiceProtocol],
    current_user: FromDishka[UserModel | None],
):
    try:
        if payload.slug:
            short_url = await url_service.create_custom_short_url(
                str(payload.long_url), str(payload.slug), current_user
            )
        else:
            short_url = await url_service.create_random_short_url(
                str(payload.long_url), current_user
            )
    except DomainErrors.ShortUrl.SlugConflictError:
        raise HTTPErrors.ShortUrl.SLUG_ALREADY_EXISTS()
    except DomainErrors.Retry.BudgetExceededError:
        raise HTTPErrors.ShortUrl.RETRIES_AMOUNT_EXCEEDED()

    return short_url
