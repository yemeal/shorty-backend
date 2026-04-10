from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class OriginCheckMiddleware(BaseHTTPMiddleware):
    """
    Minimal CSRF mitigation for cookie-auth APIs.

    For unsafe methods, if Origin header is present and not trusted -> 403.
    If Origin header is absent, request is allowed (supports curl / same-origin cases).
    """

    def __init__(self, app, trusted_origins: list[str]):
        super().__init__(app)
        self._trusted_origins = set(trusted_origins)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin is not None and origin not in self._trusted_origins:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Origin not allowed"},
                )
        return await call_next(request)

