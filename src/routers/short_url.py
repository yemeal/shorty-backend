from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, HTTPException
from starlette import status

from src.core.exceptions import RetriesAmountExceeded
from src.schemas.short_url import (
    ShortUrlCreate,
    ShortUrlResponse,
)
from src.services.url_service import AbstractUrlService

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
        Body(embed=True),
    ],
    url_service: FromDishka[AbstractUrlService],
):
    try:
        short_url = await url_service.create_short_url(str(payload.long_url))
    except RetriesAmountExceeded:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="We had problem generating short url, try again later.",
        )

    return short_url
