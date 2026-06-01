"""Run: python -m scripts.seed (from backend directory)"""
import asyncio
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.customer import Customer
from app.models.enums import OrderStatus, UserRole
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User

settings = get_settings()


async def seed() -> None:
    engine = create_async_engine(settings.database_url)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        result = await session.execute(select(User).where(User.email == settings.seed_admin_email))
        if not result.scalar_one_or_none():
            session.add(
                User(
                    email=settings.seed_admin_email,
                    hashed_password=get_password_hash(settings.seed_admin_password),
                    full_name="System Admin",
                    role=UserRole.ADMIN,
                )
            )

        cat = (
            await session.execute(select(Category).where(Category.name == "Electronics"))
        ).scalar_one_or_none()
        if not cat:
            cat = Category(name="Electronics", description="Electronic devices")
            session.add(cat)
            await session.flush()

        mouse = (
            await session.execute(select(Product).where(Product.sku == "WM-001"))
        ).scalar_one_or_none()
        if not mouse:
            mouse = Product(
                name="Wireless Mouse",
                sku="WM-001",
                description="Ergonomic wireless mouse",
                price=Decimal("29.99"),
                quantity=100,
                low_stock_threshold=10,
                category_id=cat.id,
            )
            session.add(mouse)
            await session.flush()

        hub = (await session.execute(select(Product).where(Product.sku == "HUB-002"))).scalar_one_or_none()
        if not hub:
            session.add(
                Product(
                    name="USB-C Hub",
                    sku="HUB-002",
                    description="7-in-1 USB-C hub",
                    price=Decimal("49.99"),
                    quantity=50,
                    low_stock_threshold=10,
                    category_id=cat.id,
                )
            )

        customer = (
            await session.execute(select(Customer).where(Customer.email == "demo@customer.com"))
        ).scalar_one_or_none()
        if not customer:
            customer = Customer(
                name="Demo Customer",
                email="demo@customer.com",
                phone="+1-555-0100",
                address="123 Demo Street",
            )
            session.add(customer)
            await session.flush()

        order_count = (await session.execute(select(func.count()).select_from(Order))).scalar_one()
        mouse = (await session.execute(select(Product).where(Product.sku == "WM-001"))).scalar_one_or_none()
        customer = (
            await session.execute(select(Customer).where(Customer.email == "demo@customer.com"))
        ).scalar_one_or_none()
        if order_count == 0 and mouse and customer:
            qty = 2
            line_total = mouse.price * qty
            order = Order(
                order_number="ORD-SEED001",
                customer_id=customer.id,
                status=OrderStatus.DELIVERED,
                subtotal=line_total,
                tax=Decimal("0"),
                total=line_total,
                notes="Sample seed order for demo",
            )
            session.add(order)
            await session.flush()
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=mouse.id,
                    quantity=qty,
                    unit_price=mouse.price,
                    line_total=line_total,
                )
            )
            mouse.quantity = max(0, mouse.quantity - qty)

        await session.commit()
    await engine.dispose()
    print("Seed completed.")


if __name__ == "__main__":
    asyncio.run(seed())
