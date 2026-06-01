from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.session import get_db
from app.repositories.inventory_repo import InventoryLogRepository
from app.schemas.inventory import InventoryLogOut
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.utils.responses import APIResponse

router = APIRouter()


def _log_to_out(log) -> InventoryLogOut:
    return InventoryLogOut(
        id=log.id,
        product_id=log.product_id,
        product_name=log.product.name if log.product else None,
        user_id=log.user_id,
        movement_type=log.movement_type,
        quantity_change=log.quantity_change,
        quantity_before=log.quantity_before,
        quantity_after=log.quantity_after,
        reference=log.reference,
        notes=log.notes,
        created_at=log.created_at,
        updated_at=log.updated_at,
    )


@router.get("/logs", response_model=APIResponse[PaginatedResponse[InventoryLogOut]])
async def list_inventory_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: UUID | None = None,
):
    repo = InventoryLogRepository(db)
    items, total = await repo.list_all(PaginationParams(page=page, page_size=page_size), product_id)
    return APIResponse(
        data=PaginatedResponse.create(
            [_log_to_out(i) for i in items],
            total,
            page,
            page_size,
        )
    )


@router.get("/products/{product_id}/logs", response_model=APIResponse[PaginatedResponse[InventoryLogOut]])
async def product_inventory_logs(
    product_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    repo = InventoryLogRepository(db)
    items, total = await repo.list_for_product(product_id, PaginationParams(page=page, page_size=page_size))
    return APIResponse(
        data=PaginatedResponse.create(
            [_log_to_out(i) for i in items],
            total,
            page,
            page_size,
        )
    )
