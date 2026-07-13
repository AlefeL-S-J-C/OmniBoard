import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.models import Base


def get_database_url() -> str:
    """Get database URL, handling both local and Docker environments."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # Fallback: construct from individual components
    user = os.getenv("POSTGRES_USER", "omniboard_admin")
    password = os.getenv("POSTGRES_PASSWORD", "secret_password_123")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "omniboard_db")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception:
            if attempt < 9:
                await asyncio.sleep(2)
            else:
                raise


async def close_db():
    await engine.dispose()


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
