from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import DomainErrors
from src.utils.protocols.session import AsyncSessionProtocol
from src.utils.specification import Specification


class AbstractAsyncRepository[ModelType](ABC):
    @abstractmethod
    async def add(self, entity: ModelType) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def get(self, entity_id: UUID) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: ModelType) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        *,
        specification: Specification,
    ) -> Sequence[ModelType]:
        """
        Delete all rows matching ``specification`` (must include predicates - see :class:`Specification`).

        Returns deleted ORM instances (e.g. via ``DELETE ... RETURNING``). Empty sequence if nothing matched.
        """
        raise NotImplementedError

    @abstractmethod
    async def find(
        self, specification: Specification
    ) -> Sequence[ModelType] | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(
        self, specification: Specification
    ) -> ModelType | None:
        raise NotImplementedError


class SQLAlchemyAsyncRepository[ModelType](
    AbstractAsyncRepository[ModelType]
):
    def __init__(
        self, session: AsyncSessionProtocol, model_class: type[ModelType]
    ) -> None:
        self.session = session
        self.model_class = model_class

    async def add(self, entity: ModelType) -> ModelType:
        try:
            self.session.add(entity)
            await self.session.flush()
            return entity
        except IntegrityError as e:
            raise DomainErrors.Persistence.INTEGRITY_VIOLATION(
                operation="insert",
                model=self.model_class.__name__,
                cause=e,
            ) from e

    async def get(self, entity_id: UUID) -> ModelType | None:
        return await self.session.get(self.model_class, entity_id)

    async def update(self, entity: ModelType) -> ModelType | None:
        merged_entity = await self.session.merge(entity)
        await self.session.flush()
        return merged_entity

    async def delete(
        self,
        *,
        specification: Specification,
    ) -> Sequence[ModelType]:
        stmt = delete(self.model_class)
        stmt = specification.apply(stmt)
        stmt = stmt.returning(self.model_class)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find(
        self, specification: Specification
    ) -> Sequence[ModelType] | None:
        stmt = select(self.model_class)
        stmt = specification.apply(stmt)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_one(
        self, specification: Specification
    ) -> ModelType | None:
        stmt = select(self.model_class)
        stmt = specification.apply(stmt)

        result = await self.session.execute(stmt)
        return result.scalar()
