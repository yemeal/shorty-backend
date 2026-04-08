from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column, Mapped


from src.models.base import Base, UuidMixin


class ShortUrl(Base, UuidMixin):

    short_url: Mapped[str] = mapped_column(
        String(30),
        index=True,
        unique=True,
    )
    long_url: Mapped[str] = mapped_column(
        String(20000),
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        default=None,
    )

    usage_count: Mapped[int] = mapped_column(
        default=0,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
