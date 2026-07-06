import asyncio
import os

import redis.asyncio as aioredis


class MatchmakingPool:
    def __init__(self):
        self._redis: aioredis.Redis | None = None
        self._queue_key = "matchmaking:queue"
        self._running = False
        self._interval = 2.0

    async def start(self):
        self._redis = await aioredis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True,
        )
        self._running = True
        asyncio.create_task(self._tick())

    async def stop(self):
        self._running = False

    async def enqueue(self, player_id: int, elo: float):
        await self._redis.zadd(self._queue_key, {str(player_id): elo})

    async def dequeue(self, player_id: int):
        await self._redis.zrem(self._queue_key, str(player_id))

    async def _find_match(self) -> tuple[int, int] | None:
        players = await self._redis.zrange(self._queue_key, 0, -1, withscores=True)
        if len(players) < 2:
            return None
        best_pair = None
        best_diff = float("inf")
        for i in range(len(players) - 1):
            diff = abs(players[i][1] - players[i + 1][1])
            if diff < best_diff:
                best_diff = diff
                best_pair = (int(players[i][0]), int(players[i + 1][0]))
        if best_pair:
            await self._redis.zrem(self._queue_key, str(best_pair[0]), str(best_pair[1]))
        return best_pair

    async def _tick(self):
        while self._running:
            match = await self._find_match()
            if match:
                pass
            await asyncio.sleep(self._interval)
