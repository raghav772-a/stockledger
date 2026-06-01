from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import OrderStatus
from app.schemas.common import ORMModel, TimestampSchema
from app.schemas.customer import CustomerOut
from app.schemas.product import ProductBriefOut


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: UUID
    items: list[OrderItemCreate] = Field(min_length=1)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    notes: str | None = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    notes: str | None = None


class OrderItemOut(ORMModel, TimestampSchema):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    product: ProductBriefOut | None = None


class OrderOut(ORMModel, TimestampSchema):
    id: UUID
    order_number: str
    customer_id: UUID
    status: OrderStatus
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    notes: str | None
    customer: CustomerOut | None = None
    items: list[OrderItemOut] = []
