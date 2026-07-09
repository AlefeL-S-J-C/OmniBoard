import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect(
            user="omniboard_admin",
            password="secret_password_123",
            database="postgres",
            host="localhost",
            port=5432,
        )
        result = await conn.fetchval("SELECT 1")
        print(f"Connected to postgres db: {result}")
        await conn.close()
    except Exception as e:
        print(f"postgres db error: {type(e).__name__}: {e}")

    try:
        conn = await asyncpg.connect(
            user="postgres",
            password="postgres",
            database="postgres",
            host="localhost",
            port=5432,
        )
        result = await conn.fetchval("SELECT 1")
        print(f"Connected with default user: {result}")
        await conn.close()
    except Exception as e:
        print(f"default user error: {type(e).__name__}: {e}")

asyncio.run(test())