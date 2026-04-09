from datetime import datetime
from uuid import UUID

from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.models.base import Base, UuidMixin, TimestampMixin, IsActiveMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .short_url_visit import ShortUrlVisit


class ShortUrl(Base, TimestampMixin, IsActiveMixin,  UuidMixin):

    slug: Mapped[str] = mapped_column(
        String(30),
        index=True,
        unique=True,
    )
    long_url: Mapped[str] = mapped_column(
        String(20000),
    )
    usage_count: Mapped[int] = mapped_column(
        default=0,
    )
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="short_urls")
    visits: Mapped[list["ShortUrlVisit"]] = relationship(back_populates="short_url")
