"""
Pytest Configuration and Shared Fixtures

Provides test configuration and reusable fixtures for all tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.database import Base, get_db
from backend.core.config import settings
import backend.models_db  # Register models

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_engine():
    """
    Create a test database engine for each test function.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for each test.
    """
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.
    
    Overrides the app's database dependency with the test database session.
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_sensor_data():
    """
    Sample sensor data for testing.
    """
    return {
        "id": "TEST001",
        "name": "Test Sensor",
        "location": "Test Lab",
        "source_type": "CSV",
        "organization_id": 1
    }


@pytest.fixture
def sample_readings():
    """
    Sample sensor readings for analysis.
    """
    import numpy as np
    # Generate 100 points of clean sinusoidal data
    t = np.linspace(0, 10, 100)
    values = np.sin(t) * 10 + np.random.normal(0, 0.5, 100)
    return values.tolist()


@pytest.fixture
def sample_noisy_readings():
    """
    Sample noisy sensor readings.
    """
    import numpy as np
    t = np.linspace(0, 10, 100)
    values = np.sin(t) * 10 + np.random.normal(0, 3.0, 100)
    return values.tolist()
