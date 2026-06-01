from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.session import get_db
from app.models.enums import OrderStatus
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate, OrderUpdate
from app.services.order_service import OrderService
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.utils.responses import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[OrderOut]])
async def list_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: OrderStatus | None = None,
    customer_id: UUID | None = None,
):
    result = await OrderService(db).list(
        PaginationParams(page=page, page_size=page_size), search, status, customer_id
    )
    return APIResponse(data=result)


@router.post("", response_model=APIResponse[OrderOut])
async def create_order(
    data: OrderCreate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order = await OrderService(db).create(data, user)
    return APIResponse(data=order, message="Order created")


@router.get("/{order_id}", response_model=APIResponse[OrderOut])
async def get_order(order_id: UUID, db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    order = await OrderService(db).get(order_id)
    return APIResponse(data=order)


@router.patch("/{order_id}", response_model=APIResponse[OrderOut])
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order = await OrderService(db).update(order_id, data, user)
    return APIResponse(data=order, message="Order updated")


@router.patch("/{order_id}/status", response_model=APIResponse[OrderOut])
async def update_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order = await OrderService(db).update_status(order_id, data, user)
    return APIResponse(data=order, message="Status updated")
