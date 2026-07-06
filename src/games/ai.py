import random

from src.games.base import BaseGame

FILES = "abcdefgh"


def _chess_moves(game: BaseGame, state: dict, player_id: str) -> list[dict]:
    board = state["board"]
    moves: list[dict] = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue
            color = "white" if piece.isupper() else "black"
            if color != player_id:
                continue
            moves.extend(game._get_legal_moves(board, r, c))
    return moves


def _checkers_moves(game: BaseGame, state: dict, player_id: str) -> list[dict]:
    board = state["board"]
    moves: list[dict] = []
    has_jump = False
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue
            color = "white" if piece.lower() == "w" else "black"
            if color != player_id:
                continue
            jumps = game._get_jumps(board, r, c)
            if jumps:
                has_jump = True
                moves.extend(jumps)
    if has_jump:
        return moves
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue
            color = "white" if piece.lower() == "w" else "black"
            if color != player_id:
                continue
            is_king = piece.upper() == piece
            for dr in ([-1, 1] if is_king else ([-1] if color == "white" else [1])):
                for dc in (-1, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == ".":
                        moves.append({
                            "from": f"{FILES[c]}{8-r}",
                            "to": f"{FILES[nc]}{8-nr}",
                        })
    return moves


def _reversi_moves(game: BaseGame, state: dict, player_id: str) -> list[dict]:
    board = state["board"]
    moves: list[dict] = []
    for r in range(8):
        for c in range(8):
            pos = f"{FILES[c]}{8-r}"
            if game.validate_move(state, {"position": pos}, player_id):
                moves.append({"position": pos})
    return moves


def _go_moves(game: BaseGame, state: dict, player_id: str) -> list[dict]:
    board = state["board"]
    size = len(board)
    moves: list[dict] = [{"position": "pass"}]
    for r in range(size):
        for c in range(size):
            pos = f"{FILES[c]}{size-r}"
            if game.validate_move(state, {"position": pos}, player_id):
                moves.append({"position": pos})
    return moves


def _ludo_moves(game: BaseGame, state: dict, player_id: str) -> list[dict]:
    dice = state.get("dice")
    if dice is None:
        return [{"roll": True}]
    pawns = state["pawns"][player_id]
    moves: list[dict] = []
    for i, pawn in enumerate(pawns):
        if pawn.get("done", False):
            continue
        if pawn["home"] and dice == 6:
            moves.append({"pawn_index": i})
        elif pawn.get("stretch", -1) >= 0:
            if pawn["stretch"] + dice <= 6:
                moves.append({"pawn_index": i})
        elif not pawn["home"]:
            moves.append({"pawn_index": i})
    return moves


def _trilha_moves(game: BaseGame, state: dict, player_id: str) -> list[dict]:
    board = state["board"]
    moves: list[dict] = []
    if state["removing"]:
        for pos in range(24):
            if board[pos] and board[pos] != player_id:
                moves.append({"remove": pos})
        return moves
    if state["phase"] == 1:
        for pos in range(24):
            if board[pos] is None:
                moves.append({"place": pos})
    elif state["phase"] == 2:
        for pos in range(24):
            if board[pos] == player_id:
                for adj in game._get_adjacent(pos):
                    if board[adj] is None:
                        moves.append({"from": pos, "to": adj})
    elif state["phase"] == 3:
        for pos in range(24):
            if board[pos] == player_id:
                for target in range(24):
                    if board[target] is None:
                        moves.append({"from": pos, "to": target})
    return moves


MOVE_GENERATORS = {
    "chess": _chess_moves,
    "checkers": _checkers_moves,
    "reversi": _reversi_moves,
    "go": _go_moves,
    "ludo": _ludo_moves,
    "trilha": _trilha_moves,
}


class AiPlayer:
    def __init__(self, game_type: str, game_engine: BaseGame):
        self.game_type = game_type
        self.game_engine = game_engine

    def choose_move(self, state: dict, player_id: str) -> dict | None:
        generator = MOVE_GENERATORS.get(self.game_type)
        if not generator:
            return None
        moves = generator(self.game_engine, state, player_id)
        if not moves:
            return None
        return random.choice(moves)
