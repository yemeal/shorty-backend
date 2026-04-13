import os
from dotenv import load_dotenv
from sqlalchemy.engine.url import URL
from typing import Literal

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
).render_as_string(hide_password=False)

RESERVED_SLUGS = {
    # Core app/API routes
    "docs",
    "redoc",
    "openapi.json",
    "short_url",
    "auth",
    "me",
    "api",
    "admin",
    "health",
    "metrics",
    "graphql",
    "ws",
    # Frontend SPA routes
    "login",
    "register",
    "profile",
    "placeholder",
    "profile-placeholder",
    # Common static/system paths
    "favicon.ico",
    "favicon",
    "robots.txt",
    "robots",
    "sitemap.xml",
    "sitemap",
    "manifest.webmanifest",
    "manifest",
    "assets",
    "static",
    "public",
    "img",
    "images",
    "fonts",
    "css",
    "js",
    "uploads",
    "media",
    # Marketing/service reserved words
    "about",
    "contact",
    "privacy",
    "terms",
    "support",
    "help",
    "status",
    "dashboard",
    "settings",
    "shorty",
    # Cyrillic aliases
    "апи",
    "админ",
    "доки",
    "вход",
    "регистрация",
    "профиль",
    "настройки",
}

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Fail-fast for prod safety 
if SECRET_KEY is None or SECRET_KEY.strip() == "":
    raise RuntimeError("SECRET_KEY is required")
if ALGORITHM is None or ALGORITHM.strip() == "":
    raise RuntimeError("ALGORITHM is required")

COOKIE_SECURE = os.getenv("COOKIE_SECURE") == "true"
COOKIE_SAMESITE: Literal["lax", "strict", "none"] | None = os.getenv("COOKIE_SAMESITE", "lax").lower()
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN") or None

# CSRF origin allowlist
TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "TRUSTED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000,https://шорти.рф,https://xn--h1algi1a.xn--p1ai",
    ).split(",")
    if origin.strip()
]