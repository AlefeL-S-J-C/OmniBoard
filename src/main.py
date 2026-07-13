import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Annotated, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.gateway import GatewayManager
from src.core.lobby import MatchmakingPool
from src.core.observability import init_observability
from src.database.postgres import init_db, close_db, get_session
from src.database.redis_client import init_redis, close_redis, get_redis
from src.core.security import create_token, decode_token, hash_password, verify_password
from src.games.manager import ENGINES, GameManager, MatchConfig
from src.database.models import User, Match, MatchEvent
from src.push.service import send_push

logger = logging.getLogger("omniboard")
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

gateway = GatewayManager()
matchmaking = MatchmakingPool()
game_manager = GameManager()


# ---------- Dependencies ----------
async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    # optionally verify user exists and active
    result = await db.execute(select(User).where(User.id == int(payload["sub"]), User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return {"sub": str(user.id), "username": user.username}


async def rate_limit_ws(player_id: int, limit: int = 30, window: int = 60):
    """Simple token‑bucket using Redis INCR with TTL."""
    try:
        redis = get_redis()
    except RuntimeError:
        return  # Redis not initialized, skip rate limiting
    key = f"ratelimit:ws:{player_id}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="WebSocket rate limit exceeded")


# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando OmniBoard Engine...")
    await init_db()
    await init_redis()
    await matchmaking.start()
    logger.info("OmniBoard Engine iniciado com sucesso")
    yield
    logger.info("Desligando OmniBoard Engine...")
    await close_db()
    await close_redis()
    await matchmaking.stop()
    logger.info("OmniBoard Engine desligado")


app = FastAPI(title="OmniBoard Engine", version="1.0.0", lifespan=lifespan)

init_observability(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic models ----------
class DevLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    game_type: str = "chess"
    with_ai: bool = True


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class JoinQueueRequest(BaseModel):
    game_type: str = Field(pattern="^(chess|checkers|go|ludo|reversi|trilha)$")
    with_ai: bool = False


# ---------- Health ----------
@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------- Auth ----------
@app.post("/api/auth/register")
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # check unique
    existing = await db.execute(select(User).where((User.username == body.username) | (User.email == body.email)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_token(user_id=user.id, username=user.username)
    return {"token": token, "user_id": user.id, "username": user.username}


@app.post("/api/auth/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user_id=user.id, username=user.username)
    return {"token": token, "user_id": user.id, "username": user.username}


# OAuth placeholders
@app.get("/api/auth/oauth/{provider}")
async def oauth_redirect(provider: str):
    # In a real implementation redirect to provider's OAuth URL
    return {"detail": f"OAuth flow for {provider} not implemented yet"}


@app.post("/api/auth/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: str, db: AsyncSession = Depends(get_db)):
    # Exchange code for token, fetch profile, create/get user, issue JWT
    return {"detail": f"OAuth callback for {provider} not implemented yet"}


# ---------- Dev login (keep for quick testing) ----------
_dev_user_counter = 0

@app.post("/api/dev-login")
async def dev_login(body: DevLoginRequest):
    global _dev_user_counter
    if body.game_type not in ENGINES:
        raise HTTPException(status_code=400, detail=f"Jogo não suportado: {body.game_type}")
    _dev_user_counter += 1
    token = create_token(user_id=_dev_user_counter, username=body.username)
    logger.info("Dev login: user=%s id=%d game=%s ai=%s", body.username, _dev_user_counter, body.game_type, body.with_ai)
    return {
        "token": token,
        "username": body.username,
        "user_id": _dev_user_counter,
        "game_type": body.game_type,
        "with_ai": body.with_ai,
    }


# ---------- Games list ----------
@app.get("/api/games")
async def list_games():
    return {
        "games": [
            {"id": k, "name": v.__name__.replace("Engine", "")}
            for k, v in ENGINES.items()
        ]
    }


# ---------- Matchmaking ----------
@app.post("/api/matchmaking/join")
async def join_matchmaking(body: JoinQueueRequest, user=Depends(get_current_user)):
    player_id = int(user["sub"])
    match_id = await matchmaking.join_queue(player_id, body.game_type, body.with_ai)
    if match_id:
        return {"matched": True, "match_id": match_id}
    return {"matched": False, "message": "Aguardando oponente…"}


@app.post("/api/matchmaking/leave")
async def leave_matchmaking(game_type: str, user=Depends(get_current_user)):
    player_id = int(user["sub"])
    await matchmaking.leave_queue(player_id, game_type)
    return {"detail": "Left queue"}


# ---------- FCM token ----------
class FCMTokenRequest(BaseModel):
    token: str


@app.put("/api/users/me/fcm")
async def update_fcm_token(body: FCMTokenRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    player_id = int(user["sub"])
    result = await db.execute(select(User).where(User.id == player_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.fcm_token = body.token
    await db.commit()
    return {"detail": "FCM token updated"}


# ---------- Replay ----------
@app.get("/api/matches/{match_id}/events")
async def get_match_events(match_id: str, turn: Optional[int] = Query(None), db: AsyncSession = Depends(get_db)):
    stmt = select(MatchEvent).where(MatchEvent.match_id == match_id).order_by(MatchEvent.turn)
    if turn is not None:
        stmt = stmt.where(MatchEvent.turn <= turn)
    result = await db.execute(stmt)
    events = result.scalars().all()
    return [
        {
            "turn": e.turn,
            "player": e.player,
            "action": e.action,
            "state": e.new_state,
            "timestamp": e.created_at.isoformat(),
        }
        for e in events
    ]


# ---------- WebSocket: player ----------
@app.websocket("/ws/{match_id}/{player_token}")
async def websocket_endpoint(
    websocket: WebSocket, match_id: str, player_token: str
):
    # rate limit per player (extract player_id from token)
    payload = decode_token(player_token)
    if not payload:
        await websocket.close(code=4001)
        return
    player_id = int(payload["sub"])
    try:
        await rate_limit_ws(player_id)
    except HTTPException as e:
        await websocket.close(code=4029, reason=e.detail)
        return

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
        logger.info("Jogador %d desconectado da partida %s", player_id, match_id)
        await gateway.disconnect(match_id, player_id)
    except Exception:
        logger.exception("Erro no WebSocket %s / jogador %d", match_id, player_id)
        await gateway.disconnect(match_id, player_id)


# ---------- WebSocket: spectator ----------
@app.websocket("/ws/watch/{match_id}")
async def websocket_watch(websocket: WebSocket, match_id: str, token: str = Query(...)):
    # optional auth for private matches; here we just allow any valid token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    await websocket.accept()
    # send current state
    state = game_manager.get_state(match_id)
    if not state:
        await websocket.send_json({"evento": "erro", "message": "Partida não encontrada"})
        await websocket.close()
        return
    await websocket.send_json({"evento": "estado_atual", "novo_estado": state})
    # keep connection alive, forward broadcasts from gateway (simplified: just listen for close)
    try:
        while True:
            # spectators don't send moves; just keep alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("Espectador desconectado da partida %s", match_id)
    except Exception:
        logger.exception("Erro no WebSocket espectador %s", match_id)


# ---------- Run ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)