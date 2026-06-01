import os
import uuid
from typing import Annotated
from uuid import UUID

import aiofiles
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import CurrentUser
from app.database.session import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate, StockAdjust
from app.services.product_service import ProductService
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.utils.responses import APIResponse

router = APIRouter()
settings = get_settings()


@router.get("", response_model=APIResponse[PaginatedResponse[ProductOut]])
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category_id: UUID | None = None,
    low_stock_only: bool = False,
):
    result = await ProductService(db).list(
        PaginationParams(page=page, page_size=page_size), search, category_id, low_stock_only
    )
    return APIResponse(data=result)


@router.post("", response_model=APIResponse[ProductOut])
async def create_product(
    data: ProductCreate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    product = await ProductService(db).create(data)
    return APIResponse(data=product, message="Product created")


@router.get("/{product_id}", response_model=APIResponse[ProductOut])
async def get_product(product_id: UUID, db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    product = await ProductService(db).get(product_id)
    return APIResponse(data=product)


@router.patch("/{product_id}", response_model=APIResponse[ProductOut])
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    product = await ProductService(db).update(product_id, data)
    return APIResponse(data=product)


@router.delete("/{product_id}", response_model=APIResponse[None])
async def delete_product(product_id: UUID, _: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    await ProductService(db).delete(product_id)
    return APIResponse(message="Product deleted")


@router.post("/{product_id}/stock", response_model=APIResponse[ProductOut])
async def adjust_stock(
    product_id: UUID,
    data: StockAdjust,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    product = await ProductService(db).adjust_stock(product_id, data.quantity_change, user, data.notes)
    return APIResponse(data=product)


@router.post("/{product_id}/image", response_model=APIResponse[ProductOut])
async def upload_image(
    product_id: UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    if file.size and file.size > settings.max_upload_bytes:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="File too large")
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    async with aiofiles.open(path, "wb") as out:
        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail="File too large")
        await out.write(content)
    image_url = f"/uploads/{filename}"
    product = await ProductService(db).update(product_id, ProductUpdate(image_url=image_url))
    return APIResponse(data=product)
