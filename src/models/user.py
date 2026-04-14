from src.models.base import Base, TimestampMixin, IsActiveMixin, UuidMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .short_url import ShortUrl
    from .user_profile import UserProfile


class User(Base, TimestampMixin, IsActiveMixin, UuidMixin):
    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str]
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, 
        default=None,
        unique=True,
        index=True,
    )

    short_urls: Mapped[list["ShortUrl"]] = relationship(
        back_populates="owner"
    )
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", 
        uselist=False,
        cascade="all, delete-orphan",
    )