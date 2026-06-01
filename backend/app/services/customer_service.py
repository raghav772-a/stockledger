from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer
from app.models.order import Order
from app.repositories.customer_repo import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.schemas.order import OrderOut
from app.utils.pagination import PaginatedResponse, PaginationParams


class CustomerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.customers = CustomerRepository(session)

    async def create(self, data: CustomerCreate) -> CustomerOut:
        if await self.customers.get_by_email(data.email.lower()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        payload = data.model_dump()
        payload["email"] = data.email.lower()
        customer = Customer(**payload)
        self.session.add(customer)
        await self.session.flush()
        await self.session.refresh(customer)
        return CustomerOut.model_validate(customer)

    async def update(self, id: UUID, data: CustomerUpdate) -> CustomerOut:
        customer = await self.customers.get_by_id(id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        updates = data.model_dump(exclude_unset=True)
        if "email" in updates and updates["email"]:
            updates["email"] = updates["email"].lower()
            existing = await self.customers.get_by_email(updates["email"], exclude_id=id)
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        for key, value in updates.items():
            setattr(customer, key, value)
        await self.session.flush()
        await self.session.refresh(customer)
        return CustomerOut.model_validate(customer)

    async def delete(self, id: UUID) -> None:
        customer = await self.customers.get_by_id(id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        customer.soft_delete()

    async def get(self, id: UUID) -> CustomerOut:
        customer = await self.customers.get_by_id(id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return CustomerOut.model_validate(customer)

    async def list(
        self, pagination: PaginationParams, search: str | None = None
    ) -> PaginatedResponse[CustomerOut]:
        items, total = await self.customers.list_paginated(pagination, search)
        return PaginatedResponse.create(
            [CustomerOut.model_validate(c) for c in items], total, pagination.page, pagination.page_size
        )

    async def order_history(self, id: UUID, pagination: PaginationParams) -> PaginatedResponse[OrderOut]:
        customer = await self.customers.get_by_id(id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        from sqlalchemy import func

        filters = [Order.customer_id == id, Order.deleted_at.is_(None)]
        total = (await self.session.execute(select(func.count()).select_from(Order).where(*filters))).scalar_one()
        stmt = (
            select(Order)
            .options(selectinload(Order.items), selectinload(Order.customer))
            .where(*filters)
            .order_by(Order.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        result = await self.session.execute(stmt)
        orders = list(result.unique().scalars().all())
        return PaginatedResponse.create(
            [OrderOut.model_validate(o) for o in orders], total, pagination.page, pagination.page_size
        )
