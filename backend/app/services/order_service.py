from __future__ import annotations

import secrets
from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.models.user import User
from app.repositories.customer_repo import CustomerRepository
from app.repositories.order_repo import OrderRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate, OrderUpdate
from app.services.inventory_service import InventoryService
from app.utils.pagination import PaginatedResponse, PaginationParams


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.orders = OrderRepository(session)
        self.products = ProductRepository(session)
        self.customers = CustomerRepository(session)
        self.inventory = InventoryService(session)

    def _generate_order_number(self) -> str:
        return f"ORD-{secrets.token_hex(4).upper()}"

    def _merge_items(self, items: list) -> dict[UUID, int]:
        merged: dict[UUID, int] = defaultdict(int)
        for item in items:
            merged[item.product_id] += item.quantity
        return dict(merged)

    async def _restore_order_inventory(self, order: Order, user: User) -> None:
        for item in order.items:
            product = await self.products.get_for_update(item.product_id)
            if product:
                await self.inventory.restore_for_order(
                    product, item.quantity, user, order.order_number
                )

    async def create(self, data: OrderCreate, user: User) -> OrderOut:
        customer = await self.customers.get_by_id(data.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        merged = self._merge_items(data.items)
        line_items: list[tuple] = []
        subtotal = Decimal("0")

        for product_id, qty in merged.items():
            product = await self.products.get_for_update(product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {product_id} not found",
                )
            if product.quantity < qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. Available: {product.quantity}",
                )
            line_total = product.price * qty
            subtotal += line_total
            line_items.append((product, qty, product.price, line_total))

        tax = (subtotal * data.tax_rate).quantize(Decimal("0.01"))
        total = subtotal + tax

        order = Order(
            order_number=self._generate_order_number(),
            customer_id=data.customer_id,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            tax=tax,
            total=total,
            notes=data.notes,
            created_by_id=user.id,
        )
        self.session.add(order)
        await self.session.flush()

        for product, qty, unit_price, line_total in line_items:
            self.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )
            await self.inventory.deduct_for_order(product, qty, user, order.order_number)

        await self.session.flush()
        result = await self.orders.get_detail(order.id)
        return OrderOut.model_validate(result)

    async def update_status(self, id: UUID, data: OrderStatusUpdate, user: User) -> OrderOut:
        return await self.update(id, OrderUpdate(status=data.status), user)

    async def update(self, id: UUID, data: OrderUpdate, user: User) -> OrderOut:
        order = await self.orders.get_detail(id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        old_status = order.status

        if old_status == OrderStatus.CANCELLED and data.status and data.status != OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status of a cancelled order",
            )

        if data.status is not None and data.status != old_status:
            if data.status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
                await self._restore_order_inventory(order, user)
            order.status = data.status

        if data.notes is not None:
            order.notes = data.notes

        await self.session.flush()
        result = await self.orders.get_detail(id)
        return OrderOut.model_validate(result)

    async def get(self, id: UUID) -> OrderOut:
        order = await self.orders.get_detail(id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderOut.model_validate(order)

    async def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        status: OrderStatus | None = None,
        customer_id: UUID | None = None,
    ) -> PaginatedResponse[OrderOut]:
        items, total = await self.orders.list_paginated(pagination, search, status, customer_id)
        return PaginatedResponse.create(
            [OrderOut.model_validate(o) for o in items], total, pagination.page, pagination.page_size
        )
