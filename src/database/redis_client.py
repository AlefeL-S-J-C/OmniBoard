import os

import redis.asyncio as aioredis


def get_redis_url() -> str:
    """Get Redis URL, handling both local and Docker environments."""
    url = os.getenv("REDIS_URL")
    if url:
        return url
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    return f"redis://{host}:{port}/0"


REDIS_URL = get_redis_url()

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