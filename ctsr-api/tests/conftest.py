import asyncio
import os
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.config import get_settings
from api.main import app


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create a shared async engine against the configured test database."""
    settings = get_settings()
    database_url = os.getenv("TEST_DATABASE_URL", settings.database_url)
    engine = create_async_engine(database_url, future=True)

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except OperationalError as exc:  # pragma: no cover - environmental guard
        pytest.skip(f"Test database unavailable: {exc}")

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    """Async HTTP client against the app with its own DB connection."""
    # App initializes its own engine via lifespan - both use TEST_DATABASE_URL
    async with app.router.lifespan_context(app):  # type: ignore
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as async_client:
            yield async_client


@pytest.fixture
def unique_code() -> str:
    """Generate a short unique suffix for codes to avoid uniqueness conflicts."""
    return uuid4().hex[:8]
