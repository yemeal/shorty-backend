from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from typing import Annotated

from src.database.di import get_session
from src.schemas.short_url import (
    ShortUrlCreate,
    ShortUrlResponse,
)
from src.services.url_service import UrlService

router = APIRouter(
    prefix="/short_url",
    tags=["short_url"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ShortUrlResponse,
)
async def create_short_url(
    payload: Annotated[
        ShortUrlCreate,
        Body(embed=True),
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
    url_service=Depends(UrlService),
):
    # TODO try/except
    short_url = await url_service.create_short_url(
        url=str(payload.long_url),
        db=session,
    )
    return short_url
