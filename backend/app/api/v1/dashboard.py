from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.session import get_db
from app.schemas.inventory import DashboardStats, MonthlySales, TopProduct
from app.schemas.order import OrderOut
from app.schemas.product import ProductOut
from app.services.dashboard_service import DashboardService
from app.utils.responses import APIResponse

router = APIRouter()


@router.get("/stats", response_model=APIResponse[DashboardStats])
async def stats(db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    return APIResponse(data=await DashboardService(db).stats())


@router.get("/monthly-sales", response_model=APIResponse[list[MonthlySales]])
async def monthly_sales(db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    return APIResponse(data=await DashboardService(db).monthly_sales())


@router.get("/top-products", response_model=APIResponse[list[TopProduct]])
async def top_products(db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    return APIResponse(data=await DashboardService(db).top_products())


@router.get("/recent-orders", response_model=APIResponse[list[OrderOut]])
async def recent_orders(db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    return APIResponse(data=await DashboardService(db).recent_orders())


@router.get("/low-stock", response_model=APIResponse[list[ProductOut]])
async def low_stock(db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    return APIResponse(data=await DashboardService(db).low_stock())
