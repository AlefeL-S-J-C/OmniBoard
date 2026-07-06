from copy import deepcopy

from src.games.base import BaseGame

FILES = "abcdefgh"


class ChessEngine(BaseGame):
    def get_initial_state(self) -> dict:
        board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ]
        return {
            "board": board,
            "current_player": "white",
            "castling_rights": {"K": True, "Q": True, "k": True, "q": True},
            "en_passant": None,
            "halfmove_clock": 0,
            "fullmove_number": 1,
        }

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def _find_king(self, board: list[list[str]], color: str) -> tuple[int, int] | None:
        king = "K" if color == "white" else "k"
        for r in range(8):
            for c in range(8):
                if board[r][c] == king:
                    return (r, c)
        return None

    def _is_square_attacked(
        self, board: list[list[str]], row: int, col: int, by_color: str
    ) -> bool:
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == ".":
                    continue
                color = "white" if piece.isupper() else "black"
                if color != by_color:
                    continue
                moves = self._get_piece_moves(board, r, c)
                target = f"{FILES[col]}{8-row}"
                if any(m["to"] == target for m in moves):
                    return True
        return False

    def _is_in_check(self, board: list[list[str]], color: str) -> bool:
        king_pos = self._find_king(board, color)
        if not king_pos:
            return False
        r, c = king_pos
        opponent = "black" if color == "white" else "white"
        return self._is_square_attacked(board, r, c, opponent)

    def _get_piece_moves(self, board: list[list[str]], r: int, c: int) -> list[dict]:
        piece = board[r][c]
        color = "white" if piece.isupper() else "black"
        moves = []
        p = piece.lower()

        if p == "p":
            direction = -1 if color == "white" else 1
            start_row = 6 if color == "white" else 1
            if self._in_bounds(r + direction, c) and board[r + direction][c] == ".":
                moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[c]}{8-(r+direction)}"})
                if r == start_row and board[r + 2 * direction][c] == ".":
                    moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[c]}{8-(r+2*direction)}"})
            for dc in (-1, 1):
                nr, nc = r + direction, c + dc
                if self._in_bounds(nr, nc) and board[nr][nc] != "." and \
                   (board[nr][nc].isupper() != (color == "white")):
                    moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[nc]}{8-nr}"})

        elif p == "n":
            for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                           (1, -2), (1, 2), (2, -1), (2, 1)]:
                nr, nc = r + dr, c + dc
                if self._in_bounds(nr, nc) and \
                   (board[nr][nc] == "." or board[nr][nc].isupper() != (color == "white")):
                    moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[nc]}{8-nr}"})

        elif p in ("b", "r", "q"):
            directions = []
            if p in ("r", "q"):
                directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if p in ("b", "q"):
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while self._in_bounds(nr, nc):
                    if board[nr][nc] == ".":
                        moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[nc]}{8-nr}"})
                    else:
                        if board[nr][nc].isupper() != (color == "white"):
                            moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[nc]}{8-nr}"})
                        break
                    nr += dr
                    nc += dc

        elif p == "k":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if self._in_bounds(nr, nc) and \
                       (board[nr][nc] == "." or board[nr][nc].isupper() != (color == "white")):
                        moves.append({"from": f"{FILES[c]}{8-r}", "to": f"{FILES[nc]}{8-nr}"})

        return moves

    def _get_legal_moves(self, board: list[list[str]], r: int, c: int) -> list[dict]:
        color = "white" if board[r][c].isupper() else "black"
        pseudo = self._get_piece_moves(board, r, c)
        legal = []
        for move in pseudo:
            test_board = deepcopy(board)
            c_from = FILES.index(move["from"][0])
            r_from = 8 - int(move["from"][1])
            c_to = FILES.index(move["to"][0])
            r_to = 8 - int(move["to"][1])
            test_board[r_to][c_to] = test_board[r_from][c_from]
            test_board[r_from][c_from] = "."
            if not self._is_in_check(test_board, color):
                legal.append(move)
        return legal

    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        board = current_state["board"]
        f_from = move.get("from", "")
        f_to = move.get("to", "")
        if len(f_from) != 2 or len(f_to) != 2:
            return False
        c_from, r_from = FILES.index(f_from[0]), 8 - int(f_from[1])
        piece = board[r_from][c_from]
        color = "white" if piece.isupper() else "black"
        if piece == "." or color != player_id:
            return False
        legal = self._get_legal_moves(board, r_from, c_from)
        return move in legal

    def apply_move(self, current_state: dict, move: dict) -> dict:
        new_state = deepcopy(current_state)
        board = new_state["board"]
        c_from = FILES.index(move["from"][0])
        r_from = 8 - int(move["from"][1])
        c_to = FILES.index(move["to"][0])
        r_to = 8 - int(move["to"][1])
        board[r_to][c_to] = board[r_from][c_from]
        board[r_from][c_from] = "."
        new_state["current_player"] = "black" if new_state["current_player"] == "white" else "white"
        new_state["fullmove_number"] += 1 if new_state["current_player"] == "white" else 0
        return new_state

    def _has_legal_moves(self, board: list[list[str]], color: str) -> bool:
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == ".":
                    continue
                if (piece.isupper() and color == "white") or (piece.islower() and color == "black"):
                    if self._get_legal_moves(board, r, c):
                        return True
        return False

    def check_victory(self, current_state: dict) -> str | None:
        board = current_state["board"]
        color = current_state["current_player"]
        in_check = self._is_in_check(board, color)
        has_moves = self._has_legal_moves(board, color)
        if in_check and not has_moves:
            return "black" if color == "white" else "white"
        if not in_check and not has_moves:
            return "draw"
        return None
