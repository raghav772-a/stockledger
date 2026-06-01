from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import InventoryMovementType
from app.models.inventory_log import InventoryLog
from app.models.product import Product
from app.models.user import User
from app.repositories.inventory_repo import InventoryLogRepository
from app.repositories.product_repo import ProductRepository


class InventoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.products = ProductRepository(session)
        self.logs = InventoryLogRepository(session)

    async def _log_movement(
        self,
        product: Product,
        change: int,
        movement_type: InventoryMovementType,
        user: User | None,
        reference: str | None = None,
        notes: str | None = None,
    ) -> InventoryLog:
        before = product.quantity
        after = before + change
        if after < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {before}",
            )
        product.quantity = after
        log = InventoryLog(
            product_id=product.id,
            user_id=user.id if user else None,
            movement_type=movement_type,
            quantity_change=change,
            quantity_before=before,
            quantity_after=after,
            reference=reference,
            notes=notes,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def adjust_stock(
        self,
        product_id: UUID,
        quantity_change: int,
        user: User,
        notes: str | None = None,
    ) -> Product:
        product = await self.products.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        movement = InventoryMovementType.IN if quantity_change > 0 else InventoryMovementType.ADJUSTMENT
        await self._log_movement(product, quantity_change, movement, user, notes=notes)
        await self.session.refresh(product)
        return product

    async def deduct_for_order(
        self,
        product: Product,
        quantity: int,
        user: User | None,
        order_number: str,
    ) -> None:
        await self._log_movement(
            product,
            -quantity,
            InventoryMovementType.ORDER,
            user,
            reference=order_number,
            notes=f"Order {order_number}",
        )

    async def restore_for_order(
        self,
        product: Product,
        quantity: int,
        user: User | None,
        order_number: str,
    ) -> None:
        await self._log_movement(
            product,
            quantity,
            InventoryMovementType.RETURN,
            user,
            reference=order_number,
            notes=f"Cancelled order {order_number}",
        )
