from contextlib import asynccontextmanager
from typing import Annotated

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka, FromDishka, FastapiProvider, inject
from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette import status

from src.core.exceptions import LongUrlNotFoundException
from src.core.http_exceptions import HTTPErrors
from src.core.config import TRUSTED_ORIGINS
from src.utils.protocols import UrlServiceProtocol
from src.database.provider import DatabaseProvider, ServicesProvider, UserProvider
from src.routers import short_url_router, auth_router
from src.middleware.origin_check import OriginCheckMiddleware



@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    await _app.state.dishka_container.close()


app = FastAPI(lifespan=lifespan)

#CSRF
app.add_middleware(
    OriginCheckMiddleware,
    trusted_origins=TRUSTED_ORIGINS,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=TRUSTED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(short_url_router)
app.include_router(auth_router)

container = make_async_container(
    DatabaseProvider(),
    ServicesProvider(),
    UserProvider(),
    FastapiProvider(),
)
setup_dishka(container, app)


@app.get("/me")
@inject
async def me():
    # TODO return curr user profile
    pass


@app.get("/{slug}")
@inject
async def root(
    slug: Annotated[str, Path(...)],
    url_service: FromDishka[UrlServiceProtocol],
):
    try:
        long_url = (await url_service.get_original_url(slug)).long_url
    except LongUrlNotFoundException:
        raise HTTPErrors.ShortUrl.ORIGINAL_URL_NOT_FOUND()

    return RedirectResponse(
        url=long_url,
        status_code=status.HTTP_302_FOUND,
    )
