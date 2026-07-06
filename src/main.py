from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.gateway import GatewayManager
from src.core.lobby import MatchmakingPool
from src.database.postgres import init_db, close_db
from src.database.redis_client import init_redis, close_redis
from src.core.security import create_token
from src.games.manager import ENGINES, GameManager, MatchConfig

gateway = GatewayManager()
matchmaking = MatchmakingPool()
game_manager = GameManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    await matchmaking.start()
    yield
    await close_db()
    await close_redis()
    await matchmaking.stop()


app = FastAPI(title="OmniBoard Engine", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DevLoginRequest(BaseModel):
    username: str
    game_type: str = "chess"
    with_ai: bool = True


_dev_user_counter = 0


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/dev-login")
async def dev_login(body: DevLoginRequest):
    global _dev_user_counter
    _dev_user_counter += 1
    token = create_token(user_id=_dev_user_counter, username=body.username)
    return {
        "token": token,
        "username": body.username,
        "user_id": _dev_user_counter,
        "game_type": body.game_type,
        "with_ai": body.with_ai,
    }


@app.get("/api/games")
async def list_games():
    return {
        "games": [
            {"id": k, "name": v.__name__.replace("Engine", "")}
            for k, v in ENGINES.items()
        ]
    }


@app.websocket("/ws/{match_id}/{player_token}")
async def websocket_endpoint(
    websocket: WebSocket, match_id: str, player_token: str
):
    query = websocket.query_params
    game_type = query.get("game_type", "chess")
    with_ai = query.get("with_ai", "true").lower() == "true"

    player = await gateway.authenticate(player_token)
    if not player:
        await websocket.close(code=4001)
        return

    player_id = int(player["sub"])

    await gateway.connect(websocket, match_id, player_id)

    if not game_manager.get_state(match_id):
        config = MatchConfig(game_type=game_type, with_ai=with_ai)
        game_manager.create_match(match_id, config)

    state = game_manager.get_state(match_id)
    player_color = gateway.get_player_color(match_id, player_id)
    await gateway.send_to(match_id, player_id, {
        "evento": "conexao_estabelecida",
        "novo_estado": state,
        "sua_cor": player_color,
        "jogador_id": player_id,
        "game_type": game_type,
        "with_ai": with_ai,
        "message": "Bem-vindo à partida!",
    })

    try:
        while True:
            data = await websocket.receive_json()
            await gateway.handle_message(match_id, player_id, data, game_manager)
    except WebSocketDisconnect:
        await gateway.disconnect(match_id, player_id)
