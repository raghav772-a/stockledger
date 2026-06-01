from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def list_all(self) -> list[Category]:
        stmt = select(Category).where(Category.deleted_at.is_(None)).order_by(Category.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name, Category.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
