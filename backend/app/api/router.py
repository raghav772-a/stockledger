from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.customers import router as customers_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.orders import router as orders_router
from app.api.v1.products import router as products_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(customers_router, prefix="/customers", tags=["Customers"])
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])