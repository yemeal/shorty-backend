from typing import Annotated

from fastapi import FastAPI, Path, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi.middleware.cors import CORSMiddleware

from src.database.di import get_session
from src.routers import router as short_url_router
from src.services.url_service import UrlService

app = FastAPI()

app.include_router(short_url_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local Vite frontend
        "http://localhost:8000",  # Swagger/Local backend
        "https://шорти.рф",       # Production domain (just in case)
        "https://xn--h1algi1a.xn--p1ai" # Punycode production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/{slug}")
async def root(
    slug: Annotated[str, Path(...)],
    session: Annotated[AsyncSession, Depends(get_session)],
    url_service: UrlService = Depends(UrlService),
):
    # TODO try/excepts
    long_url = (
        await url_service.get_long_url_by_short_url(slug, session)
    ).long_url

    return RedirectResponse(
        url=long_url, status_code=status.HTTP_302_FOUND
    )
