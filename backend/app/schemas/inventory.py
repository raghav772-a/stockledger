from uuid import UUID

from pydantic import BaseModel

from app.models.enums import InventoryMovementType
from app.schemas.common import ORMModel, TimestampSchema


class InventoryLogOut(ORMModel, TimestampSchema):
    id: UUID
    product_id: UUID
    product_name: str | None = None
    user_id: UUID | None
    movement_type: InventoryMovementType
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reference: str | None
    notes: str | None


class DashboardStats(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    total_revenue: float
    low_stock_count: int


class MonthlySales(BaseModel):
    month: str
    revenue: float
    orders: int


class TopProduct(BaseModel):
    product_id: UUID
    product_name: str
    total_sold: int
    revenue: float
