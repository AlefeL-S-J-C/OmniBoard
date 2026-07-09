import asyncio
from src.database.postgres import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            print("Connection successful")
    except Exception as e:
        print(f"Connection error: {e}")

asyncio.run(test_connection())