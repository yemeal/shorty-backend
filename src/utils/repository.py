from abc import ABC, abstractmethod
from typing import Sequence

from sqlalchemy import select

from src.utils import AsyncSessionProtocol, Specification


class AbstractAsyncRepository[ModelType](ABC):
    @abstractmethod
    async def add(self, entity: ModelType) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, entity_id: int) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: ModelType) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: ModelType) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def find(
            self, specification: Specification[ModelType]
    ) -> Sequence[ModelType] | None:
        raise NotImplementedError


class SQLAlchemyAsyncRepository[ModelType](
    AbstractAsyncRepository[ModelType]
):
    def __init__(
            self, session: AsyncSessionProtocol, model_class: type[ModelType]
    ) -> None:
        self.session = session
        self.model_class = model_class

    async def add(self, entity: ModelType) -> ModelType | None:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get(self, entity_id: int) -> ModelType | None:
        return await self.session.get(self.model_class, entity_id)

    async def update(self, entity: ModelType) -> ModelType | None:
        merged_entity = await self.session.merge(entity)
        await self.session.flush()
        return merged_entity

    async def delete(self, entity: ModelType) -> ModelType | None:
        await self.session.delete(entity)
        return entity

    async def find(
            self, specification: Specification[ModelType]
    ) -> Sequence[ModelType] | None:
        stmt = select(self.model_class)
        stmt = specification.apply(stmt)

        result = await self.session.execute(stmt)
        return await result.scalars().all()
