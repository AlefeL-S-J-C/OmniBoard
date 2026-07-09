import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://omniboard_admin:secret_password_123@localhost:5432/omniboard_db")

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
