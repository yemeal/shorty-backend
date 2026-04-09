from src.models.base import Base, TimestampMixin, IsActiveMixin, UuidMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship      
from sqlalchemy import String, func, ForeignKey
from uuid import UUID
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .short_url import ShortUrl
    from .user import User

class ShortUrlVisit(Base, UuidMixin):

    short_url_id: Mapped[UUID] = mapped_column(ForeignKey("short_urls.id"))

    visited_at: Mapped[datetime] = mapped_column(server_default=func.now())
    country: Mapped[str | None] = mapped_column(String(255))
    device_type: Mapped[str | None] = mapped_column(String(255))

    short_url: Mapped["ShortUrl"] = relationship(back_populates="visits")
    
