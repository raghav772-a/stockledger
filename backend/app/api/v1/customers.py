from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.session import get_db
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.schemas.order import OrderOut
from app.services.customer_service import CustomerService
from app.utils.pagination import PaginatedResponse, PaginationParams
from app.utils.responses import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[CustomerOut]])
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
):
    result = await CustomerService(db).list(PaginationParams(page=page, page_size=page_size), search)
    return APIResponse(data=result)


@router.post("", response_model=APIResponse[CustomerOut])
async def create_customer(
    data: CustomerCreate,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    customer = await CustomerService(db).create(data)
    return APIResponse(data=customer, message="Customer created")


@router.get("/{customer_id}", response_model=APIResponse[CustomerOut])
async def get_customer(customer_id: UUID, db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    customer = await CustomerService(db).get(customer_id)
    return APIResponse(data=customer)


@router.patch("/{customer_id}", response_model=APIResponse[CustomerOut])
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    customer = await CustomerService(db).update(customer_id, data)
    return APIResponse(data=customer)


@router.delete("/{customer_id}", response_model=APIResponse[None])
async def delete_customer(
    customer_id: UUID, _: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    await CustomerService(db).delete(customer_id)
    return APIResponse(message="Customer deleted")


@router.get("/{customer_id}/orders", response_model=APIResponse[PaginatedResponse[OrderOut]])
async def customer_orders(
    customer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    result = await CustomerService(db).order_history(
        customer_id, PaginationParams(page=page, page_size=page_size)
    )
    return APIResponse(data=result)
