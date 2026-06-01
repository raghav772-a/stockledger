from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.session import get_db
from app.schemas.product import CategoryCreate, CategoryOut
from app.services.product_service import ProductService
from app.utils.responses import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[list[CategoryOut]])
async def list_categories(db: Annotated[AsyncSession, Depends(get_db)], _: CurrentUser):
    categories = await ProductService(db).list_categories()
    return APIResponse(data=[CategoryOut.model_validate(c) for c in categories])


@router.post("", response_model=APIResponse[CategoryOut])
async def create_category(
    data: CategoryCreate,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    category = await ProductService(db).create_category(data)
    return APIResponse(data=CategoryOut.model_validate(category))
