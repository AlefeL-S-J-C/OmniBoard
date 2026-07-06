from copy import deepcopy

from src.games.base import BaseGame

BOARD_SIZE = 9


class GoEngine(BaseGame):
    def get_initial_state(self) -> dict:
        board = [["."] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        return {
            "board": board,
            "current_player": "black",
            "captures": {"black": 0, "white": 0},
            "ko": None,
            "consecutive_passes": 0,
        }

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def _get_group(self, board: list[list[str]], r: int, c: int) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        color = board[r][c]
        if color == ".":
            return set(), set()
        visited = set()
        liberties = set()
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = cr + dr, cc + dc
                if not self._in_bounds(nr, nc):
                    continue
                if board[nr][nc] == ".":
                    liberties.add((nr, nc))
                elif board[nr][nc] == color and (nr, nc) not in visited:
                    stack.append((nr, nc))
        return visited, liberties

    def _count_territory(self, board: list[list[str]]) -> dict[str, int]:
        visited = set()
        territory = {"B": 0, "W": 0}
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] != "." or (r, c) in visited:
                    continue
                group = set()
                borders = set()
                stack = [(r, c)]
                while stack:
                    cr, cc = stack.pop()
                    if (cr, cc) in visited:
                        continue
                    if board[cr][cc] != ".":
                        continue
                    visited.add((cr, cc))
                    group.add((cr, cc))
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = cr + dr, cc + dc
                        if not self._in_bounds(nr, nc):
                            continue
                        if board[nr][nc] == ".":
                            stack.append((nr, nc))
                        else:
                            borders.add(board[nr][nc])
                if len(borders) == 1:
                    owner = borders.pop()
                    territory[owner] += len(group)
        return territory

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        board = current_state["board"]
        color = "B" if player_id == "black" else "W"
        pos = move.get("position", "")
        if pos == "pass":
            return True
        try:
            c = ord(pos[0]) - 97
            r = BOARD_SIZE - int(pos[1:])
        except (ValueError, IndexError):
            return False
        if not self._in_bounds(r, c) or board[r][c] != ".":
            return False
        if current_state.get("ko") == pos:
            return False
        test_board = deepcopy(board)
        test_board[r][c] = color
        group, libs = self._get_group(test_board, r, c)
        if libs:
            return True
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if not self._in_bounds(nr, nc):
                continue
            if test_board[nr][nc] not in ("B", "W"):
                continue
            if test_board[nr][nc] != color:
                g, l = self._get_group(test_board, nr, nc)
                if not l:
                    return True
        return False

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        board = new_state["board"]
        player_id = new_state["current_player"]
        color = "B" if player_id == "black" else "W"
        pos = move.get("position", "")
        if pos == "pass":
            new_state["consecutive_passes"] += 1
            new_state["current_player"] = "white" if player_id == "black" else "black"
            return new_state
        new_state["consecutive_passes"] = 0
        c = ord(pos[0]) - 97
        r = BOARD_SIZE - int(pos[1:])
        board[r][c] = color
        captured = 0
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if not self._in_bounds(nr, nc):
                continue
            if board[nr][nc] not in ("B", "W"):
                continue
            if board[nr][nc] != color:
                g, l = self._get_group(board, nr, nc)
                if not l:
                    for gr, gc in g:
                        board[gr][gc] = "."
                        captured += 1
        new_state["captures"][player_id] += captured
        new_state["ko"] = pos if captured == 1 else None
        new_state["current_player"] = "white" if player_id == "black" else "black"
        return new_state

    def check_victory(self, current_state: dict) -> str | None:
        if current_state["consecutive_passes"] < 2:
            return None
        territory = self._count_territory(current_state["board"])
        b_score = current_state["captures"]["black"] + territory["B"]
        w_score = current_state["captures"]["white"] + territory["W"]
        if b_score > w_score:
            return "black"
        elif w_score > b_score:
            return "white"
        return "draw"
