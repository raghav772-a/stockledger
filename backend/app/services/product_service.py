from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.repositories.category_repo import CategoryRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.product import CategoryCreate, ProductCreate, ProductOut, ProductUpdate
from app.services.inventory_service import InventoryService
from app.utils.pagination import PaginatedResponse, PaginationParams


def product_to_out(product: Product) -> ProductOut:
    out = ProductOut.model_validate(product)
    out.is_low_stock = product.quantity <= product.low_stock_threshold
    return out


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.products = ProductRepository(session)
        self.categories = CategoryRepository(session)
        self.inventory = InventoryService(session)

    async def create(self, data: ProductCreate) -> ProductOut:
        if await self.products.get_by_sku(data.sku):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
        if data.category_id:
            cat = await self.categories.get_by_id(data.category_id)
            if not cat:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        product = Product(**data.model_dump())
        self.session.add(product)
        await self.session.flush()
        result = await self.products.get_with_category(product.id)
        return product_to_out(result)

    async def update(self, id: UUID, data: ProductUpdate) -> ProductOut:
        product = await self.products.get_with_category(id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        updates = data.model_dump(exclude_unset=True)
        if "sku" in updates and updates["sku"]:
            updates["sku"] = updates["sku"].strip().upper()
            existing = await self.products.get_by_sku(updates["sku"], exclude_id=id)
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
        for key, value in updates.items():
            setattr(product, key, value)
        await self.session.flush()
        await self.session.refresh(product)
        return product_to_out(product)

    async def delete(self, id: UUID) -> None:
        product = await self.products.get_by_id(id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        product.soft_delete()

    async def get(self, id: UUID) -> ProductOut:
        product = await self.products.get_with_category(id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product_to_out(product)

    async def list(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        category_id: UUID | None = None,
        low_stock_only: bool = False,
    ) -> PaginatedResponse[ProductOut]:
        items, total = await self.products.list_paginated(pagination, search, category_id, low_stock_only)
        return PaginatedResponse.create(
            [product_to_out(p) for p in items], total, pagination.page, pagination.page_size
        )

    async def create_category(self, data: CategoryCreate) -> Category:
        if await self.categories.get_by_name(data.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
        category = Category(**data.model_dump())
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def list_categories(self) -> list[Category]:
        return await self.categories.list_all()

    async def adjust_stock(self, id: UUID, quantity_change: int, user: User, notes: str | None) -> ProductOut:
        product = await self.inventory.adjust_stock(id, quantity_change, user, notes)
        result = await self.products.get_with_category(product.id)
        return product_to_out(result)
