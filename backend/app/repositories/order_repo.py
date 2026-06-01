from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.repositories.base import BaseRepository
from app.utils.filters import apply_search
from app.utils.pagination import PaginationParams


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)

    def _base_stmt(self):
        return select(Order).options(
            selectinload(Order.customer),
            selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.category),
        )

    async def list_paginated(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        status: OrderStatus | None = None,
        customer_id: UUID | None = None,
    ) -> tuple[list[Order], int]:
        filters = [Order.deleted_at.is_(None)]
        if status:
            filters.append(Order.status == status)
        if customer_id:
            filters.append(Order.customer_id == customer_id)

        stmt = self._base_stmt().where(*filters)
        stmt = apply_search(stmt, [Order.order_number], search)

        count_stmt = select(func.count()).select_from(Order).where(*filters)
        count_stmt = apply_search(count_stmt, [Order.order_number], search)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Order.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all()), total

    async def get_detail(self, id: UUID) -> Order | None:
        stmt = self._base_stmt().where(Order.id == id, Order.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def recent(self, limit: int = 10) -> list[Order]:
        stmt = (
            self._base_stmt()
            .where(Order.deleted_at.is_(None))
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
