from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base import BaseRepository
from app.utils.filters import apply_search
from app.utils.pagination import PaginationParams


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    def _base_stmt(self):
        return select(Product).options(selectinload(Product.category))

    async def get_for_update(self, id: UUID) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == id, Product.deleted_at.is_(None))
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str, exclude_id: UUID | None = None) -> Product | None:
        stmt = select(Product).where(Product.sku == sku.upper(), Product.deleted_at.is_(None))
        if exclude_id:
            stmt = stmt.where(Product.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        category_id: UUID | None = None,
        low_stock_only: bool = False,
    ) -> tuple[list[Product], int]:
        filters = [Product.deleted_at.is_(None)]
        if category_id:
            filters.append(Product.category_id == category_id)
        if low_stock_only:
            filters.append(Product.quantity <= Product.low_stock_threshold)

        stmt = self._base_stmt().where(*filters)
        stmt = apply_search(stmt, [Product.name, Product.sku, Product.description], search)

        count_stmt = select(func.count()).select_from(Product).where(*filters)
        count_stmt = apply_search(count_stmt, [Product.name, Product.sku], search)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Product.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def get_with_category(self, id: UUID) -> Product | None:
        stmt = self._base_stmt().where(Product.id == id, Product.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def low_stock_products(self, limit: int = 10) -> list[Product]:
        stmt = (
            self._base_stmt()
            .where(Product.deleted_at.is_(None), Product.quantity <= Product.low_stock_threshold)
            .order_by(Product.quantity.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
