import os

import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: aioredis.Redis | None = None


async def init_redis():
    global _redis
    _redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    await _redis.ping()


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis


async def set_board_state(match_id: str, state: dict):
    await get_redis().hset(f"match:{match_id}", mapping=state)


async def get_board_state(match_id: str) -> dict:
    return await get_redis().hgetall(f"match:{match_id}")


async def delete_match(match_id: str):
    await get_redis().delete(f"match:{match_id}")