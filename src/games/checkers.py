from copy import deepcopy

from src.games.base import BaseGame


class CheckersEngine(BaseGame):
    def get_initial_state(self) -> dict:
        board = [["."] * 8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    if r < 3:
                        board[r][c] = "b"
                    elif r > 4:
                        board[r][c] = "w"
        return {
            "board": board,
            "current_player": "white",
        }

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def _is_king(self, piece: str) -> bool:
        return piece.upper() == piece

    def _get_jumps(self, board: list[list[str]], r: int, c: int) -> list[dict]:
        piece = board[r][c]
        jumps = []
        directions = self._get_directions(piece)
        for dr, dc in directions:
            mr, mc = r + dr, c + dc
            lr, lc = r + 2 * dr, c + 2 * dc
            if self._in_bounds(lr, lc) and board[mr][mc] != "." and board[lr][lc] == ".":
                target = board[mr][mc]
                if target.lower() != piece.lower():
                    jumps.append({
                        "from": f"{chr(97+c)}{8-r}",
                        "to": f"{chr(97+lc)}{8-lr}",
                        "capture": f"{chr(97+mc)}{8-mr}",
                    })
        return jumps

    def _get_directions(self, piece: str) -> list[tuple[int, int]]:
        if piece.lower() == "w":
            return [(-1, -1), (-1, 1)] if not self._is_king(piece) else [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return [(1, -1), (1, 1)] if not self._is_king(piece) else [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def _find_capture(self, board: list[list[str]], frm: str, to: str, piece: str) -> str | None:
        cf, rf = ord(frm[0]) - 97, 8 - int(frm[1])
        ct, rt = ord(to[0]) - 97, 8 - int(to[1])
        mid_r, mid_c = (rf + rt) // 2, (cf + ct) // 2
        if self._in_bounds(mid_r, mid_c) and board[mid_r][mid_c] != ".":
            target = board[mid_r][mid_c]
            if target.lower() != piece.lower():
                return f"{chr(97+mid_c)}{8-mid_r}"
        return None

    def _has_any_jump(self, board: list[list[str]], color: str) -> bool:
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p == ".":
                    continue
                pc = "white" if p.lower() == "w" else "black"
                if pc == color and self._get_jumps(board, r, c):
                    return True
        return False

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        board = current_state["board"]
        color = player_id
        c_from = ord(move["from"][0]) - 97
        r_from = 8 - int(move["from"][1])
        c_to = ord(move["to"][0]) - 97
        r_to = 8 - int(move["to"][1])
        piece = board[r_from][c_from]
        piece_color = "white" if piece.lower() == "w" else "black"
        if piece == "." or piece_color != color:
            return False

        dr, dc = r_to - r_from, c_to - c_from

        if self._has_any_jump(board, color):
            jumps = self._get_jumps(board, r_from, c_from)
            if not jumps:
                return False
            return any(m["to"] == move["to"] for m in jumps)

        if abs(dr) == 1 and abs(dc) == 1 and board[r_to][c_to] == ".":
            if self._is_king(piece):
                return True
            if piece.lower() == "w" and dr == -1:
                return True
            if piece.lower() == "b" and dr == 1:
                return True
        return False

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        board = new_state["board"]
        c_from = ord(move["from"][0]) - 97
        r_from = 8 - int(move["from"][1])
        c_to = ord(move["to"][0]) - 97
        r_to = 8 - int(move["to"][1])
        piece = board[r_from][c_from]

        capture = self._find_capture(board, move["from"], move["to"], piece)
        if capture:
            cc = ord(capture[0]) - 97
            cr = 8 - int(capture[1])
            board[cr][cc] = "."

        board[r_to][c_to] = piece
        board[r_from][c_from] = "."

        if piece.lower() == "w" and r_to == 0:
            board[r_to][c_to] = "W"
        elif piece.lower() == "b" and r_to == 7:
            board[r_to][c_to] = "B"

        new_state["current_player"] = "black" if new_state["current_player"] == "white" else "white"
        return new_state

    def check_victory(self, current_state: dict) -> str | None:
        board = current_state["board"]
        white = any("w" in c.lower() for row in board for c in row)
        black = any("b" in c.lower() for row in board for c in row)
        if not white:
            return "black"
        if not black:
            return "white"
        return None
