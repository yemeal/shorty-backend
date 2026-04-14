from sqlalchemy.orm import mapped_column, Mapped, ForeignKey, relationship
from sqlalchemy import String
from uuid import UUID
from typing import Literal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

from src.models.base import Base, UuidMixin, TimestampMixin



class UserProfile(Base, UuidMixin, TimestampMixin):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    emoji_avatar: Mapped[str] = mapped_column(String(50), default="⚡️")
    ui_theme: Mapped[Literal["light", "dark", "system"]] = mapped_column(
        default="system",   
    )
    ui_language: Mapped[Literal["en", "ru"]] = mapped_column(
        default="en",
    )
    
    bio: Mapped[str | None] = mapped_column(String(255), default=None)
    timezone: Mapped[str | None] = mapped_column(String(50), default=None)

    user: Mapped["User"] = relationship(back_populates="profile")