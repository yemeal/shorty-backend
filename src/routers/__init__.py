from .short_url import router as short_url_router
from .auth import router as auth_router
from .user import router as user_router

__all__ = (
    "short_url_router",
    "auth_router",
    "user_router",
)
