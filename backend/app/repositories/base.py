from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base, SoftDeleteMixin

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]):
        self.session = session
        self.model = model

    def _not_deleted(self, stmt):
        if issubclass(self.model, SoftDeleteMixin):
            return stmt.where(self.model.deleted_at.is_(None))
        return stmt

    async def get_by_id(self, id: UUID) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == id)
        stmt = self._not_deleted(stmt)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count(self, stmt=None) -> int:
        base = stmt if stmt is not None else select(self.model)
        base = self._not_deleted(base)
        count_stmt = select(func.count()).select_from(base.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one()
