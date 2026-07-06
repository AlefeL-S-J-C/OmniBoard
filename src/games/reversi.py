from copy import deepcopy

from src.games.base import BaseGame

BOARD_SIZE = 8
DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


class ReversiEngine(BaseGame):
    def get_initial_state(self) -> dict:
        board = [["."] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        board[3][3] = board[4][4] = "W"
        board[3][4] = board[4][3] = "B"
        return {
            "board": board,
            "current_player": "black",
        }

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def _color(self, player_id: str) -> str:
        return "B" if player_id == "black" else "W"

    def _opponent(self, player_id: str) -> str:
        return "W" if player_id == "black" else "B"

    def _flips_for(self, board: list[list[str]], r: int, c: int, player_id: str) -> list[tuple[int, int]]:
        color = self._color(player_id)
        opp = self._opponent(player_id)
        if board[r][c] != ".":
            return []
        flips = []
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            candidates = []
            while self._in_bounds(nr, nc) and board[nr][nc] == opp:
                candidates.append((nr, nc))
                nr += dr
                nc += dc
            if self._in_bounds(nr, nc) and board[nr][nc] == color:
                flips.extend(candidates)
        return flips

    def _has_any_move(self, board: list[list[str]], player_id: str) -> bool:
        return any(
            self._flips_for(board, i, j, player_id)
            for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)
            if board[i][j] == "."
        )

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        board = current_state["board"]
        pos = move.get("position", "")
        if len(pos) != 2:
            return False
        c = ord(pos[0]) - 97
        r = 8 - int(pos[1])
        if not self._in_bounds(r, c):
            return False
        flips = self._flips_for(board, r, c, player_id)
        return len(flips) > 0

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        board = new_state["board"]
        player_id = new_state["current_player"]
        pos = move["position"]
        c = ord(pos[0]) - 97
        r = 8 - int(pos[1])
        color = self._color(player_id)
        flips = self._flips_for(board, r, c, player_id)
        board[r][c] = color
        for fr, fc in flips:
            board[fr][fc] = color
        opponent = "white" if player_id == "black" else "black"
        opponent_has_move = self._has_any_move(board, opponent)
        new_state["current_player"] = opponent if opponent_has_move else player_id
        return new_state

    def check_victory(self, current_state: dict) -> str | None:
        board = current_state["board"]
        has_empty = any(cell == "." for row in board for cell in row)
        if has_empty:
            player = current_state["current_player"]
            opponent = "white" if player == "black" else "black"
            if self._has_any_move(board, player) or self._has_any_move(board, opponent):
                return None
        b_count = sum(row.count("B") for row in board)
        w_count = sum(row.count("W") for row in board)
        if b_count > w_count:
            return "black"
        elif w_count > b_count:
            return "white"
        return "draw"
