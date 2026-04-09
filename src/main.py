from contextlib import asynccontextmanager
from typing import Annotated

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka, FromDishka, inject
from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette import status

from src.core.exceptions import LongUrlNotFoundException
from src.database.provider import DatabaseProvider, ServicesProvider
from src.routers import router as short_url_router
from src.services.url_service import AbstractUrlService


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await app.state.dishka_container.close()


app = FastAPI(lifespan=lifespan)

app.include_router(short_url_router)

container = make_async_container(
    DatabaseProvider(),
    ServicesProvider(),
)
setup_dishka(container, app)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local Vite frontend
        "http://localhost:8000",  # Swagger/Local backend
        "https://шорти.рф",  # Production domain (just in case)
        "https://xn--h1algi1a.xn--p1ai",  # Punycode production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/{slug}")
@inject
async def root(
    slug: Annotated[str, Path(...)],
    url_service: FromDishka[AbstractUrlService],
):
    try:
        # Lowercase for case-insensitive matching
        long_url = (await url_service.get_original_url(slug.lower())).long_url
    except LongUrlNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original URL not found",
        )

    return RedirectResponse(
        url=long_url,
        status_code=status.HTTP_302_FOUND,
    )
