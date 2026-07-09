import asyncio
import os
import uuid

import redis.asyncio as aioredis

from src.games.manager import game_manager, MatchConfig
from src.database.postgres import get_session
from src.database.models import Match
from sqlalchemy import select


class MatchmakingPool:
    def __init__(self):
        self._redis: aioredis.Redis | None = None
        self._queue_key = "matchmaking:queue"
        self._running = False
        self._interval = 2.0
        # per-game queues: {game_type: [player_id, ...]}
        self._queues: dict[str, list[int]] = {}

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

    async def join_queue(self, player_id: int, game_type: str, with_ai: bool = False) -> str | None:
        """Add player to per-game queue. If a pair is formed, create match and return match_id."""
        q = self._queues.setdefault(game_type, [])
        if player_id in q:
            return None
        q.append(player_id)

        if len(q) >= 2:
            p1 = q.pop(0)
            p2 = q.pop(0)
            match_id = str(uuid.uuid4())
            config = MatchConfig(game_type=game_type, with_ai=with_ai, player_white_id=p1, player_black_id=p2)
            game_manager.create_match(match_id, config)

            # persist match metadata
            async for session in get_session():
                m = Match(
                    id=match_id,
                    game_type=game_type,
                    player_white=str(p1),
                    player_black=str(p2),
                    player_white_id=p1,
                    player_black_id=p2,
                )
                session.add(m)
                await session.commit()
                break

            return match_id
        return None

    async def leave_queue(self, player_id: int, game_type: str):
        q = self._queues.get(game_type, [])
        if player_id in q:
            q.remove(player_id)

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
                pass  # legacy global queue not used now
            await asyncio.sleep(self._interval)
