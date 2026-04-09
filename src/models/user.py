from src.models.base import Base, TimestampMixin, IsActiveMixin, UuidMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .short_url import ShortUrl


class User(Base, TimestampMixin, IsActiveMixin,  UuidMixin):
    username: Mapped[str] = mapped_column(
        String(20), 
        unique=True,
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True
    )    
    hashed_password: Mapped[str]

    short_urls: Mapped[list["ShortUrl"]] = relationship(
        back_populates="owner"
    )
