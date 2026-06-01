from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.inventory_log import InventoryLog
from app.models.product import Product
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginationParams


class InventoryLogRepository(BaseRepository[InventoryLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, InventoryLog)

    async def list_all(
        self,
        pagination: PaginationParams,
        product_id: UUID | None = None,
    ) -> tuple[list[InventoryLog], int]:
        filters = []
        if product_id:
            filters.append(InventoryLog.product_id == product_id)
        count_stmt = select(func.count()).select_from(InventoryLog)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = (await self.session.execute(count_stmt)).scalar_one()
        stmt = (
            select(InventoryLog)
            .options(joinedload(InventoryLog.product))
            .order_by(InventoryLog.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        if filters:
            stmt = stmt.where(*filters)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all()), total

    async def list_for_product(
        self,
        product_id: UUID,
        pagination: PaginationParams,
    ) -> tuple[list[InventoryLog], int]:
        filters = [InventoryLog.product_id == product_id]
        total = (
            await self.session.execute(select(func.count()).select_from(InventoryLog).where(*filters))
        ).scalar_one()
        stmt = (
            select(InventoryLog)
            .options(joinedload(InventoryLog.product))
            .where(*filters)
            .order_by(InventoryLog.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all()), total
