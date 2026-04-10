from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, HTTPException
from starlette import status

from src.core.exceptions import (
    RetriesAmountExceeded,
    SlugAlreadyExistsException,
)
from src.utils.protocols import UrlServiceProtocol
from src.models import User as UserModel
from src.schemas.short_url import (
    ShortUrlCreate,
    ShortUrlResponse,
)

router = APIRouter(
    prefix="/short_url",
    tags=["short_url"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ShortUrlResponse,
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
    except SlugAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This short url already exists.",
        )
    except RetriesAmountExceeded:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="We had problem generating short url, try again later.",
        )

    return short_url
