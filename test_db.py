import asyncio
from src.database.postgres import init_db

async def test_db():
    try:
        await init_db()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")

asyncio.run(test_db())