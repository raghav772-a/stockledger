from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel, TimestampSchema


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryOut(ORMModel, TimestampSchema):
    id: UUID
    name: str
    description: str | None


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=64)
    description: str | None = None
    price: Decimal = Field(gt=0)
    quantity: int = Field(ge=0, default=0)
    low_stock_threshold: int = Field(ge=0, default=10)
    category_id: UUID | None = None

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, v: str) -> str:
        return v.strip().upper()


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)
    category_id: UUID | None = None
    image_url: str | None = None


class ProductBriefOut(ORMModel):
    """Lightweight product for nested responses (orders, etc.)."""

    id: UUID
    name: str
    sku: str
    price: Decimal | None = None
    quantity: int | None = None


class ProductOut(ORMModel, TimestampSchema):
    id: UUID
    name: str
    sku: str
    description: str | None
    price: Decimal
    quantity: int
    low_stock_threshold: int
    image_url: str | None
    category_id: UUID | None
    category: CategoryOut | None = None
    is_low_stock: bool = False


class StockAdjust(BaseModel):
    quantity_change: int
    notes: str | None = None
