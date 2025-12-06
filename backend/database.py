from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL
# For Dev: SQLite (Async)
# For Prod: PostgreSQL (Async) -> "postgresql+asyncpg://user:password@host/db"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./qorsense.db")

# Create Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Set to False in production
    future=True
)

# Create Async Session Factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit=False
)

# Declarative Base for Models
Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
