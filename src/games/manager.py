import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSON

from src.database.postgres import get_session
from src.database.models import Match, MatchEvent
from src.push.service import send_push

from src.games.ai import AiPlayer
from src.games.base import BaseGame
from src.games.chess import ChessEngine
from src.games.checkers import CheckersEngine
from src.games.go import GoEngine
from src.games.ludo import LudoEngine
from src.games.reversi import ReversiEngine
from src.games.trilha import TrilhaEngine
from src.games.rules import RulesRegistry, load_all_rules

ENGINES = {
    "chess": ChessEngine,
    "checkers": CheckersEngine,
    "go": GoEngine,
    "ludo": LudoEngine,
    "reversi": ReversiEngine,
    "trilha": TrilhaEngine,
}

# Initialize the rules registry - the core now knows all rules!
_rules_registry = RulesRegistry()
load_all_rules(_rules_registry)


def get_rules_registry() -> RulesRegistry:
    """Retorna o registro central de regras - o núcleo conhece cada regra."""
    return _rules_registry


def get_game_rules(game_type: str):
    """Retorna as regras declarativas de um jogo."""
    return _rules_registry.get(game_type)


def list_known_games() -> list[str]:
    """Lista todos os jogos que o núcleo conhece."""
    return _rules_registry.list()


AI_COLORS = ["black"]

LUDO_COLOR_MAP = {"white": "red", "black": "green"}
LUDO_COLOR_REVERSE = {
    "red": "white",
    "green": "black",
    "yellow": "white",
    "blue": "black",
}


def _normalize_player(game_type: str, player_id: str) -> str:
    if game_type == "ludo":
        return LUDO_COLOR_MAP.get(player_id, player_id)
    return player_id


def _denormalize_player(game_type: str, ludo_color: str) -> str:
    if game_type == "ludo":
        return LUDO_COLOR_REVERSE.get(ludo_color, ludo_color)
    return ludo_color


class MatchConfig:
    def __init__(self, game_type: str, with_ai: bool = True, player_white_id: int | None = None, player_black_id: int | None = None):
        engine_cls = ENGINES.get(game_type)
        if not engine_cls:
            raise ValueError(f"Jogo desconhecido: {game_type}")
        self.game_type = game_type
        self.engine = engine_cls()
        self.with_ai = with_ai
        self.player_white_id = player_white_id
        self.player_black_id = player_black_id


class GameManager:
    def __init__(self):
        self._configs: dict[str, MatchConfig] = {}
        self._instances: dict[str, BaseGame] = {}
        self._states: dict[str, dict] = {}
        self._ai_players: dict[str, AiPlayer] = {}

    def create_match(self, match_id: str, config: MatchConfig) -> dict:
        self._configs[match_id] = config
        self._instances[match_id] = config.engine
        state = config.engine.get_initial_state()
        self._states[match_id] = state
        if config.with_ai:
            self._ai_players[match_id] = AiPlayer(config.game_type, config.engine)
        return state

    def get_state(self, match_id: str) -> dict | None:
        return self._states.get(match_id)

    def get_config(self, match_id: str) -> MatchConfig | None:
        return self._configs.get(match_id)

    async def process_move(
        self, match_id: str, move: dict, player_id: str
    ) -> tuple[bool, dict | None, str | None, dict | None]:
        game = self._instances.get(match_id)
        if not game:
            return False, None, "Partida não encontrada", None

        current = self._states.get(match_id)
        if not current:
            return False, None, "Estado da partida não encontrado", None

        config = self._configs.get(match_id)
        game_type = config.game_type if config else "chess"
        internal_id = _normalize_player(game_type, player_id)

        if self._get_current_player(current) != internal_id:
            return False, None, "Não é seu turno", None

        if not game.validate_move(current, move, internal_id):
            return False, None, "Jogada inválida", None

        new_state = game.apply_move(current, move)
        self._states[match_id] = new_state
        await self._persist_event(match_id, player_id, move, new_state)

        # notify opponent via push if opponent is human
        if config and not config.with_ai:
            opponent_internal = new_state.get("current_player")
            if opponent_internal == "white":
                opponent_user_id = config.player_white_id
            elif opponent_internal == "black":
                opponent_user_id = config.player_black_id
            else:
                opponent_user_id = None
            if opponent_user_id:
                asyncio.create_task(send_push(opponent_user_id, "Sua vez!", f"O adversário jogou."))

        winner = game.check_victory(new_state)
        ai_move = None

        if winner is None and self._has_ai_turn(match_id, new_state):
            ai_move = await asyncio.to_thread(self._run_ai_sync, match_id, new_state)
            if ai_move:
                if game.validate_move(new_state, ai_move, new_state.get("current_player", "")):
                    new_state = game.apply_move(new_state, ai_move)
                    self._states[match_id] = new_state
                    await self._persist_event(match_id, "ai", ai_move, new_state)
                    winner = game.check_victory(new_state)
                else:
                    ai_move = None

        if winner:
            new_state["vencedor"] = _denormalize_player(game_type, winner)

        return True, new_state, winner, ai_move

    async def roll_dice(self, match_id: str, player_id: str) -> tuple[dict, int] | None:
        game = self._instances.get(match_id)
        if not game:
            return None
        current = self._states.get(match_id)
        if not current:
            return None
        config = self._configs.get(match_id)
        game_type = config.game_type if config else "chess"
        internal_id = _normalize_player(game_type, player_id)
        if self._get_current_player(current) != internal_id:
            return None
        if current.get("dice") is not None:
            return None
        dice = game._roll_dice()
        new_state = {**current, "dice": dice}
        self._states[match_id] = new_state
        return new_state, dice

    def _get_current_player(self, state: dict) -> str:
        return state.get("current_player", "white")

    def _has_ai_turn(self, match_id: str, state: dict) -> bool:
        ai = self._ai_players.get(match_id)
        if not ai:
            return False
        config = self._configs.get(match_id)
        if not config:
            return False
        internal = _normalize_player(config.game_type, AI_COLORS[0])
        return state.get("current_player") in [internal]

    def _run_ai_sync(self, match_id: str, state: dict) -> dict | None:
        ai = self._ai_players.get(match_id)
        if not ai:
            return None
        config = self._configs.get(match_id)
        if not config:
            return None

        player_id = state.get("current_player", "")

        if state.get("dice") is None and config.game_type == "ludo":
            game = self._instances.get(match_id)
            if game:
                dice = game._roll_dice()
                state["dice"] = dice

        return ai.choose_move(state, player_id)

    def restart_match(self, match_id: str) -> dict | None:
        config = self._configs.get(match_id)
        if not config:
            return None
        state = config.engine.get_initial_state()
        self._states[match_id] = state
        return state

    async def _persist_event(self, match_id: str, player_id: str, move: dict, new_state: dict):
        try:
            async for session in get_session():
                result = await session.execute(select(Match).where(Match.id == match_id))
                match = result.scalar_one_or_none()
                if not match:
                    match = Match(id=match_id, game_type=self._configs[match_id].game_type)
                    session.add(match)
                    await session.flush()
                turn = len(match.events) + 1
                event = MatchEvent(
                    match_id=match.id,
                    turn=turn,
                    player=player_id,
                    action=str(move),
                    new_state=new_state,
                )
                session.add(event)
                await session.commit()
                break
        except Exception as e:
            print(f"[persist] failed for match {match_id}: {e}")


game_manager = GameManager()