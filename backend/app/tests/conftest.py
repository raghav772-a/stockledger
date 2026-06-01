import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/inventory_test")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql+psycopg2://postgres:postgres@localhost:5432/inventory_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long")

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
