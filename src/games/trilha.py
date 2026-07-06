from copy import deepcopy

from src.games.base import BaseGame

BOARD_POSITIONS = list(range(24))
MILLS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
    [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23],
    [0, 9, 21], [3, 10, 18], [6, 11, 15], [1, 4, 7],
    [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23],
]
PLAYER_PIECES = 9

PHASE_PLACEMENT = 1
PHASE_MOVEMENT = 2
PHASE_FLYING = 3


class TrilhaEngine(BaseGame):
    def get_initial_state(self) -> dict:
        return {
            "board": {p: None for p in BOARD_POSITIONS},
            "players": {
                "white": {"pieces_in_hand": PLAYER_PIECES, "pieces_on_board": 0},
                "black": {"pieces_in_hand": PLAYER_PIECES, "pieces_on_board": 0},
            },
            "current_player": "white",
            "phase": PHASE_PLACEMENT,
            "removing": False,
        }

    def _forms_mill(self, board: dict, player_id: str, pos: int) -> bool:
        for mill in MILLS:
            if pos in mill and all(board[p] == player_id for p in mill):
                return True
        return False

    def _can_remove(self, board: dict, player_id: str, pos: int) -> bool:
        if board[pos] is None or board[pos] == player_id:
            return False
        opponent = "black" if player_id == "white" else "white"
        for mill in MILLS:
            if pos in mill and all(board[p] == opponent for p in mill):
                return False
        return True

    def _get_adjacent(self, pos: int) -> list[int]:
        adj = {
            0: [1, 9], 1: [0, 2, 4], 2: [1, 14],
            3: [4, 10], 4: [1, 3, 5, 7], 5: [4, 13],
            6: [7, 11], 7: [4, 6, 8], 8: [7, 12],
            9: [0, 10, 21], 10: [3, 9, 11, 18], 11: [6, 10, 15],
            12: [8, 13, 17], 13: [5, 12, 14, 20], 14: [2, 13, 23],
            15: [11, 16], 16: [15, 17, 19], 17: [12, 16],
            18: [10, 19], 19: [16, 18, 20, 22], 20: [13, 19],
            21: [9, 22], 22: [19, 21, 23], 23: [14, 22],
        }
        return adj.get(pos, [])

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        board = current_state["board"]
        if current_state["removing"]:
            return "remove" in move and self._can_remove(board, player_id, move["remove"])
        if current_state["phase"] == PHASE_PLACEMENT:
            return "place" in move and move["place"] in BOARD_POSITIONS and board[move["place"]] is None
        if current_state["phase"] == PHASE_MOVEMENT:
            if "from" not in move or "to" not in move:
                return False
            if board[move["from"]] != player_id or board[move["to"]] is not None:
                return False
            return move["to"] in self._get_adjacent(move["from"])
        if current_state["phase"] == PHASE_FLYING:
            if "from" not in move or "to" not in move:
                return False
            return board[move["from"]] == player_id and board[move["to"]] is None
        return False

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        board = new_state["board"]
        player_id = new_state["current_player"]

        if new_state["removing"]:
            board[move["remove"]] = None
            opponent = "black" if player_id == "white" else "white"
            new_state["players"][opponent]["pieces_on_board"] -= 1
            new_state["removing"] = False
            return new_state

        pos = None
        if "place" in move:
            pos = move["place"]
            board[pos] = player_id
            new_state["players"][player_id]["pieces_in_hand"] -= 1
            new_state["players"][player_id]["pieces_on_board"] += 1
            if new_state["players"][player_id]["pieces_in_hand"] == 0:
                new_state["phase"] = PHASE_MOVEMENT
        elif "from" in move and "to" in move:
            board[move["to"]] = board[move["from"]]
            board[move["from"]] = None
            pos = move["to"]
            if new_state["phase"] == PHASE_MOVEMENT and \
               new_state["players"][player_id]["pieces_on_board"] == 3:
                new_state["phase"] = PHASE_FLYING

        if pos is not None and self._forms_mill(board, player_id, pos):
            new_state["removing"] = True
        else:
            new_state["current_player"] = "black" if player_id == "white" else "white"

        return new_state

    def check_victory(self, current_state: dict) -> str | None:
        for pid in ("white", "black"):
            if current_state["players"][pid]["pieces_on_board"] < 3 and current_state["phase"] != PHASE_PLACEMENT:
                return "black" if pid == "white" else "white"
        return None
