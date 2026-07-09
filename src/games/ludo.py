import secrets
from copy import deepcopy

from src.games.base import BaseGame

# Tamanho da pista principal (casas por volta do tabuleiro). 50 casas para casar
# com o grid 15x15 renderizado no front-end.
BOARD_SIZE = 50
PLAYERS = ["red", "green", "yellow", "blue"]
PAWNS_PER_PLAYER = 4
# Posicao de entrada na pista principal para cada cor.
HOME_ENTRY = {"red": 0, "green": 13, "yellow": 25, "blue": 38}
# Casas seguras (estrelas). Pawns em casas seguras nao podem ser capturados.
SAFE_SPOTS = {0, 8, 13, 21, 25, 33, 38, 46}
PLAYER_ORDER = {"red": 0, "green": 1, "yellow": 2, "blue": 3}

GATEWAY_TO_LUDO = {"white": "red", "black": "green"}
LUDO_TO_GATEWAY = {
    "red": "white",
    "green": "black",
    "yellow": "white",
    "blue": "black",
}

STRETCH_LENGTH = 6


def _initial_pawn() -> dict:
    return {
        "pos": -1,
        "home": True,
        "progress": -1,
        "stretch": -1,
        "done": False,
    }


class LudoEngine(BaseGame):
    def get_initial_state(self) -> dict:
        return {
            "pawns": {
                p: [deepcopy(_initial_pawn()) for _ in range(PAWNS_PER_PLAYER)]
                for p in PLAYERS
            },
            "current_player": "red",
            "dice": None,
        }

    def _roll_dice(self) -> int:
        return secrets.randbelow(6) + 1

    def _board_pos(self, progress: int, player: str) -> int:
        if progress < 0:
            return -1
        return (HOME_ENTRY[player] + progress) % BOARD_SIZE

    def _is_safe(self, bpos: int) -> bool:
        return bpos in SAFE_SPOTS

    @staticmethod
    def _pawn_can_move(pawn: dict, dice: int) -> bool:
        """Verifica se um dado pawn pode se mover com o valor do dado atual."""
        if pawn.get("done", False):
            return False
        if pawn.get("home", True):
            return dice == 6
        stretch = pawn.get("stretch", -1)
        if stretch >= 0:
            return stretch + dice <= STRETCH_LENGTH
        progress = pawn.get("progress", -1)
        final_progress = BOARD_SIZE - 1
        if progress + dice > final_progress:
            # O peao ja completou a volta; o excedente entraria na reta final,
            # mas como ele ja esta passando, so e valido se couber na stretch
            # (que tem STRETCH_LENGTH casas). Computa o overshoot da pista
            # completa: casa 0 da reta e a posicao final-progress+1.
            overshoot = progress + dice - (final_progress + 1)
            return overshoot < STRETCH_LENGTH
        return True

    def _can_player_move(self, state: dict, player: str, dice: int) -> bool:
        return any(
            self._pawn_can_move(p, dice) for p in state["pawns"][player]
        )

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        ludo_id = GATEWAY_TO_LUDO.get(player_id, player_id)
        if ludo_id not in current_state.get("pawns", {}):
            return False
        if current_state["current_player"] != ludo_id:
            return False
        dice = current_state.get("dice")
        if dice is None:
            return False
        pawn_idx = move.get("pawn_index", -1)
        if not isinstance(pawn_idx, int) or pawn_idx < 0 or pawn_idx >= PAWNS_PER_PLAYER:
            return False
        pawn = current_state["pawns"][ludo_id][pawn_idx]
        return self._pawn_can_move(pawn, int(dice))

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        player = new_state["current_player"]
        pawn = new_state["pawns"][player][move["pawn_index"]]
        dice = new_state["dice"]
        if not isinstance(dice, int):
            return new_state

        captured = False
        bonus_turn = dice == 6

        if pawn["home"]:
            pawn["home"] = False
            pawn["progress"] = 0
            pawn["stretch"] = -1
            pawn["pos"] = self._board_pos(0, player)
            captured = self._try_capture(new_state, player, pawn["pos"], safe=False)
        elif pawn.get("stretch", -1) >= 0:
            pawn["stretch"] += dice
            if pawn["stretch"] >= STRETCH_LENGTH:
                pawn["done"] = True
                pawn["stretch"] = -1
                pawn["pos"] = -1
        else:
            old_progress = pawn["progress"]
            new_progress = old_progress + dice
            final_progress = BOARD_SIZE - 1
            if new_progress > final_progress:
                overshoot = new_progress - (final_progress + 1)
                pawn["progress"] = final_progress + 1
                pawn["stretch"] = overshoot
                pawn["pos"] = -1
                if pawn["stretch"] >= STRETCH_LENGTH:
                    pawn["done"] = True
                    pawn["stretch"] = -1
            else:
                pawn["progress"] = new_progress
                pawn["pos"] = self._board_pos(new_progress, player)
                captured = self._try_capture(
                    new_state, player, pawn["pos"], safe=self._is_safe(pawn["pos"])
                )

        new_state["dice"] = None
        if bonus_turn or captured:
            new_state["current_player"] = player
        else:
            current_idx = PLAYER_ORDER[player]
            new_state["current_player"] = PLAYERS[(current_idx + 1) % 4]
        return new_state

    def _try_capture(self, state: dict, owner: str, bpos: int, safe: bool) -> bool:
        if bpos < 0 or safe:
            return False
        captured = False
        for other in PLAYERS:
            if other == owner:
                continue
            for op in state["pawns"][other]:
                if (
                    not op.get("home", True)
                    and not op.get("done", False)
                    and op.get("stretch", -1) < 0
                    and op.get("pos", -1) == bpos
                ):
                    op["pos"] = -1
                    op["home"] = True
                    op["progress"] = -1
                    op["stretch"] = -1
                    captured = True
        return captured

    def check_victory(self, current_state: dict) -> str | None:
        for p in PLAYERS:
            if all(pawn.get("done", False) for pawn in current_state["pawns"][p]):
                return p
        return None

    def has_any_move(self, state: dict, player_id: str) -> bool:
        dice = state.get("dice")
        if dice is None:
            return False
        return self._can_player_move(state, player_id, int(dice))
