from datetime import datetime, timezone

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.repositories.order_repo import OrderRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.inventory import DashboardStats, MonthlySales, TopProduct
from app.schemas.order import OrderOut
from app.schemas.product import ProductOut
from app.services.product_service import product_to_out

ACTIVE_ORDER_FILTER = (Order.deleted_at.is_(None), Order.status != OrderStatus.CANCELLED)


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.orders = OrderRepository(session)
        self.products = ProductRepository(session)

    async def stats(self) -> DashboardStats:
        product_count = (
            await self.session.execute(
                select(func.count()).select_from(Product).where(Product.deleted_at.is_(None))
            )
        ).scalar_one()
        customer_count = (
            await self.session.execute(
                select(func.count()).select_from(Customer).where(Customer.deleted_at.is_(None))
            )
        ).scalar_one()
        order_count = (
            await self.session.execute(
                select(func.count()).select_from(Order).where(Order.deleted_at.is_(None))
            )
        ).scalar_one()
        revenue = (
            await self.session.execute(
                select(func.coalesce(func.sum(Order.total), 0))
                .select_from(Order)
                .where(*ACTIVE_ORDER_FILTER)
            )
        ).scalar_one()
        low_stock = (
            await self.session.execute(
                select(func.count()).select_from(Product).where(
                    Product.deleted_at.is_(None),
                    Product.quantity <= Product.low_stock_threshold,
                )
            )
        ).scalar_one()
        return DashboardStats(
            total_products=int(product_count or 0),
            total_customers=int(customer_count or 0),
            total_orders=int(order_count or 0),
            total_revenue=float(revenue or 0),
            low_stock_count=int(low_stock or 0),
        )

    async def monthly_sales(self, months: int = 6) -> list[MonthlySales]:
        now = datetime.now(timezone.utc)
        results: list[MonthlySales] = []
        for i in range(months - 1, -1, -1):
            month = now.month - i
            year = now.year
            while month <= 0:
                month += 12
                year -= 1
            period_filters = (
                *ACTIVE_ORDER_FILTER,
                extract("month", Order.created_at) == month,
                extract("year", Order.created_at) == year,
            )
            revenue = float(
                (
                    await self.session.execute(
                        select(func.coalesce(func.sum(Order.total), 0))
                        .select_from(Order)
                        .where(*period_filters)
                    )
                ).scalar_one()
                or 0
            )
            orders = (
                await self.session.execute(
                    select(func.count()).select_from(Order).where(*period_filters)
                )
            ).scalar_one()
            results.append(
                MonthlySales(month=f"{year}-{month:02d}", revenue=revenue, orders=int(orders or 0))
            )
        return results

    async def top_products(self, limit: int = 5) -> list[TopProduct]:
        stmt = (
            select(
                OrderItem.product_id,
                Product.name,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.line_total).label("revenue"),
            )
            .join(Product, Product.id == OrderItem.product_id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                *ACTIVE_ORDER_FILTER,
                Product.deleted_at.is_(None),
            )
            .group_by(OrderItem.product_id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            TopProduct(
                product_id=row.product_id,
                product_name=row.name,
                total_sold=int(row.total_sold or 0),
                revenue=float(row.revenue or 0),
            )
            for row in rows
        ]

    async def recent_orders(self, limit: int = 10) -> list[OrderOut]:
        orders = await self.orders.recent(limit)
        return [OrderOut.model_validate(o) for o in orders]

    async def low_stock(self, limit: int = 10) -> list[ProductOut]:
        products = await self.products.low_stock_products(limit)
        return [product_to_out(p) for p in products]
