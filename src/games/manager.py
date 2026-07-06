from src.games.ai import AiPlayer
from src.games.base import BaseGame
from src.games.chess import ChessEngine
from src.games.checkers import CheckersEngine
from src.games.go import GoEngine
from src.games.ludo import LudoEngine
from src.games.reversi import ReversiEngine
from src.games.trilha import TrilhaEngine

ENGINES = {
    "chess": ChessEngine,
    "checkers": CheckersEngine,
    "go": GoEngine,
    "ludo": LudoEngine,
    "reversi": ReversiEngine,
    "trilha": TrilhaEngine,
}

AI_COLORS = ["black"]

# Ludo uses its own internal player colors (red,green,yellow,blue)
# but the gateway passes white/black. Map them here.
LUDO_COLOR_MAP = {"white": "red", "black": "green"}
LUDO_COLOR_REVERSE = {"red": "white", "green": "black", "yellow": "white", "blue": "black"}


def _normalize_player(game_type: str, player_id: str) -> str:
    if game_type == "ludo":
        return LUDO_COLOR_MAP.get(player_id, player_id)
    return player_id


def _denormalize_player(game_type: str, ludo_color: str) -> str:
    if game_type == "ludo":
        return LUDO_COLOR_REVERSE.get(ludo_color, ludo_color)
    return ludo_color


class MatchConfig:
    def __init__(self, game_type: str, with_ai: bool = True):
        engine_cls = ENGINES.get(game_type)
        if not engine_cls:
            raise ValueError(f"Jogo desconhecido: {game_type}")
        self.game_type = game_type
        self.engine = engine_cls()
        self.with_ai = with_ai


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
            self._ai_players[match_id] = AiPlayer(
                config.game_type, config.engine
            )
        return state

    def get_state(self, match_id: str) -> dict | None:
        return self._states.get(match_id)

    def get_config(self, match_id: str) -> MatchConfig | None:
        return self._configs.get(match_id)

    def process_move(
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

        if current["current_player"] != internal_id:
            return False, None, "Não é seu turno", None

        if not game.validate_move(current, move, internal_id):
            return False, None, "Jogada inválida", None

        new_state = game.apply_move(current, move)
        self._states[match_id] = new_state

        winner = game.check_victory(new_state)
        ai_move = None

        if winner is None and self._has_ai_turn(match_id, new_state):
            ai_move = self._run_ai(match_id, new_state)
            if ai_move and game.validate_move(new_state, ai_move, new_state["current_player"]):
                new_state = game.apply_move(new_state, ai_move)
                self._states[match_id] = new_state
                winner = game.check_victory(new_state)

        if winner:
            new_state["vencedor"] = _denormalize_player(game_type, winner)

        return True, new_state, winner, ai_move

    def roll_dice(self, match_id: str, player_id: str) -> tuple[dict, int] | None:
        game = self._instances.get(match_id)
        if not game:
            return None
        current = self._states.get(match_id)
        if not current:
            return None
        config = self._configs.get(match_id)
        game_type = config.game_type if config else "chess"
        internal_id = _normalize_player(game_type, player_id)
        if current.get("current_player") != internal_id:
            return None
        if current.get("dice") is not None:
            return None
        dice = game._roll_dice()
        new_state = {**current, "dice": dice}
        self._states[match_id] = new_state
        return new_state, dice

    def _has_ai_turn(self, match_id: str, state: dict) -> bool:
        ai = self._ai_players.get(match_id)
        if not ai:
            return False
        config = self._configs.get(match_id)
        if not config:
            return False
        internal = _normalize_player(config.game_type, AI_COLORS[0])
        return state["current_player"] in [internal]

    def _run_ai(self, match_id: str, state: dict) -> dict | None:
        ai = self._ai_players.get(match_id)
        if not ai:
            return None
        config = self._configs.get(match_id)
        if not config:
            return None

        player_id = state["current_player"]

        if state.get("dice") is None and config.game_type == "ludo":
            game = self._instances.get(match_id)
            if not game:
                return None
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

    def remove_match(self, match_id: str):
        self._configs.pop(match_id, None)
        self._instances.pop(match_id, None)
        self._states.pop(match_id, None)
        self._ai_players.pop(match_id, None)
