"""Supabase Postgres async engine."""
import os
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = structlog.get_logger()

_db_url = os.getenv("SUPABASE_DB_URL")
if not _db_url:
    raise ValueError("SUPABASE_DB_URL not set")

# Convert postgres:// to postgresql+asyncpg://
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif not _db_url.startswith("postgresql+asyncpg://"):
    _db_url = f"postgresql+asyncpg://{_db_url}"

engine = create_async_engine(_db_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        yield session

