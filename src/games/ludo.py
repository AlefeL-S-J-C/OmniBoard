import secrets
from copy import deepcopy

from src.games.base import BaseGame

BOARD_SIZE = 50
PLAYERS = ["red", "green", "yellow", "blue"]
PAWNS_PER_PLAYER = 4
HOME_POSITIONS = {"red": 0, "green": 13, "yellow": 25, "blue": 38}
SAFE_ZONES = {0, 8, 13, 21, 25, 33, 38, 46}
PLAYER_ORDER = {"red": 0, "green": 1, "yellow": 2, "blue": 3}

GATEWAY_TO_LUDO = {"white": "red", "black": "green"}
LUDO_TO_GATEWAY = {"red": "white", "green": "black"}


class LudoEngine(BaseGame):
    def get_initial_state(self) -> dict:
        return {
            "pawns": {p: [{"pos": -1, "home": True, "progress": -1, "stretch": -1, "done": False}
                        for _ in range(PAWNS_PER_PLAYER)]
                     for p in PLAYERS},
            "current_player": "red",
            "dice": None,
        }

    def _roll_dice(self) -> int:
        return secrets.randbelow(6) + 1

    def _board_pos(self, progress: int, player: str) -> int:
        if progress < 0:
            return -1
        return (HOME_POSITIONS[player] + progress) % BOARD_SIZE

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        ludo_id = GATEWAY_TO_LUDO.get(player_id, player_id)
        dice = current_state.get("dice")
        if dice is None:
            return False
        pawn_idx = move.get("pawn_index", -1)
        if pawn_idx < 0 or pawn_idx >= PAWNS_PER_PLAYER:
            return False
        pawn = current_state["pawns"][ludo_id][pawn_idx]
        if pawn.get("done", False):
            return False
        if pawn["home"]:
            return dice == 6
        if pawn.get("stretch", -1) >= 0:
            return pawn["stretch"] + dice <= 6
        return True

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        player_id = new_state["current_player"]
        pawn_idx = move["pawn_index"]
        pawn = new_state["pawns"][player_id][pawn_idx]
        dice = new_state["dice"]

        if pawn["home"] and dice == 6:
            pawn["progress"] = 0
            pawn["home"] = False
            pawn["stretch"] = -1
            pawn["pos"] = self._board_pos(0, player_id)
            for other in PLAYERS:
                if other == player_id:
                    continue
                for op in new_state["pawns"][other]:
                    if not op["home"] and not op.get("done", False) and op["pos"] == pawn["pos"]:
                        op["pos"] = -1
                        op["home"] = True
                        op["progress"] = -1
        elif pawn.get("stretch", -1) >= 0:
            pawn["stretch"] += dice
            if pawn["stretch"] == 6:
                pawn["done"] = True
                pawn["pos"] = -1
                pawn["stretch"] = -1
                pawn["home"] = True
        elif not pawn["home"]:
            new_progress = pawn["progress"] + dice
            if new_progress >= BOARD_SIZE:
                overshoot = new_progress - BOARD_SIZE
                if overshoot < 6:
                    pawn["stretch"] = overshoot
                    pawn["pos"] = -1
                else:
                    return new_state
            else:
                pawn["progress"] = new_progress
                pawn["pos"] = self._board_pos(new_progress, player_id)
                for other in PLAYERS:
                    if other == player_id:
                        continue
                    for op in new_state["pawns"][other]:
                        if not op["home"] and not op.get("done", False) and op.get("stretch", -1) < 0 and op["pos"] == pawn["pos"] and pawn["pos"] not in SAFE_ZONES:
                            op["pos"] = -1
                            op["home"] = True
                            op["progress"] = -1

        new_state["dice"] = None
        if dice != 6:
            current_idx = PLAYER_ORDER[player_id]
            new_state["current_player"] = PLAYERS[(current_idx + 1) % 4]
        else:
            new_state["current_player"] = player_id
        return new_state

    def check_victory(self, current_state: dict) -> str | None:
        for p in PLAYERS:
            if all(pawn.get("done", False) for pawn in current_state["pawns"][p]):
                return p
        return None
