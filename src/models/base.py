import uuid

from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    mapped_column,
    Mapped,
)
import re


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return (
            f"{re.sub(r'([a-z])([A-Z])', r'\1_\2', cls.__name__).lower()}s"
        )


class UuidMixin:
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
    )
