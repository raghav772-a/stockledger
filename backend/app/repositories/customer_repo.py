from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.base import BaseRepository
from app.utils.filters import apply_search
from app.utils.pagination import PaginationParams


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Customer)

    async def get_by_email(self, email: str, exclude_id: UUID | None = None) -> Customer | None:
        stmt = select(Customer).where(Customer.email == email, Customer.deleted_at.is_(None))
        if exclude_id:
            stmt = stmt.where(Customer.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        pagination: PaginationParams,
        search: str | None = None,
    ) -> tuple[list[Customer], int]:
        stmt = select(Customer).where(Customer.deleted_at.is_(None))
        stmt = apply_search(stmt, [Customer.name, Customer.email, Customer.phone], search)

        count_stmt = apply_search(
            select(func.count()).select_from(Customer).where(Customer.deleted_at.is_(None)),
            [Customer.name, Customer.email],
            search,
        )
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Customer.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total
