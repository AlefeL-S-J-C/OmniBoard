from src.games.chess import ChessEngine
from src.games.checkers import CheckersEngine
from src.games.go import GoEngine
from src.games.ludo import LudoEngine
from src.games.trilha import TrilhaEngine
from src.games.reversi import ReversiEngine


def test_chess_initial_state():
    engine = ChessEngine()
    state = engine.get_initial_state()
    assert state["current_player"] == "white"
    assert len(state["board"]) == 8
    assert state["board"][0][0] == "r"


def test_chess_valid_move():
    engine = ChessEngine()
    state = engine.get_initial_state()
    move = {"from": "e2", "to": "e4"}
    assert engine.validate_move(state, move, "white") is True


def test_chess_invalid_move():
    engine = ChessEngine()
    state = engine.get_initial_state()
    move = {"from": "e2", "to": "e5"}
    assert engine.validate_move(state, move, "white") is False


def test_chess_wrong_color():
    engine = ChessEngine()
    state = engine.get_initial_state()
    move = {"from": "e2", "to": "e4"}
    assert engine.validate_move(state, move, "black") is False


def test_chess_apply_move_switches_turn():
    engine = ChessEngine()
    state = engine.get_initial_state()
    move = {"from": "e2", "to": "e4"}
    new_state = engine.apply_move(state, move)
    assert new_state["current_player"] == "black"
    assert new_state["board"][4][4] == "P"
    assert new_state["board"][6][4] == "."


def test_checkers_initial_state():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    assert state["current_player"] == "white"
    assert state["board"][0][1] == "b"


def test_checkers_white_moves_first():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    move = {"from": "a3", "to": "b4"}
    assert engine.validate_move(state, move, "white") is True


def test_checkers_apply_move():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    move = {"from": "a3", "to": "b4"}
    new_state = engine.apply_move(state, move)
    assert new_state["board"][4][1] == "w"
    assert new_state["board"][5][0] == "."
    assert new_state["current_player"] == "black"


def test_checkers_backward_move_invalid():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    state = engine.apply_move(state, {"from": "a3", "to": "b4"})
    state = engine.apply_move(state, {"from": "b6", "to": "a5"})
    assert engine.validate_move(state, {"from": "b4", "to": "a3"}, "white") is False


def test_checkers_capture_required():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    state["board"][4][1] = "b"
    state["board"][5][0] = "w"
    state["board"][3][2] = "."
    assert engine.validate_move(state, {"from": "a3", "to": "b4"}, "white") is False
    assert engine.validate_move(state, {"from": "a3", "to": "c5"}, "white") is True


def test_checkers_victory_white_wins():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    state["board"] = [["."] * 8 for _ in range(8)]
    state["board"][0][1] = "w"
    state["board"][0][3] = "w"
    assert engine.check_victory(state) == "white"


def test_checkers_victory_black_wins():
    engine = CheckersEngine()
    state = engine.get_initial_state()
    state["board"] = [["."] * 8 for _ in range(8)]
    state["board"][0][1] = "b"
    assert engine.check_victory(state) == "black"


def test_go_initial_state():
    engine = GoEngine()
    state = engine.get_initial_state()
    assert state["current_player"] == "black"
    assert len(state["board"]) == 9


def test_go_valid_move():
    engine = GoEngine()
    state = engine.get_initial_state()
    move = {"position": "d4"}
    assert engine.validate_move(state, move, "black") is True


def test_go_apply_move():
    engine = GoEngine()
    state = engine.get_initial_state()
    move = {"position": "d4"}
    new_state = engine.apply_move(state, move)
    board = new_state["board"]
    assert board[5][3] == "B"
    assert new_state["current_player"] == "white"


def test_go_pass():
    engine = GoEngine()
    state = engine.get_initial_state()
    move = {"position": "pass"}
    new_state = engine.apply_move(state, move)
    assert new_state["current_player"] == "white"
    assert new_state["consecutive_passes"] == 1


def test_ludo_initial_state():
    engine = LudoEngine()
    state = engine.get_initial_state()
    assert state["current_player"] == "red"
    assert all(p["home"] for p in state["pawns"]["red"])
    assert state["dice"] is None


def test_ludo_validate_needs_dice():
    engine = LudoEngine()
    state = engine.get_initial_state()
    move = {"pawn_index": 0}
    assert engine.validate_move(state, move, "red") is False


def test_ludo_apply_move_with_dice():
    engine = LudoEngine()
    state = engine.get_initial_state()
    state["dice"] = 6
    move = {"pawn_index": 0}
    new_state = engine.apply_move(state, move)
    assert new_state["pawns"]["red"][0]["home"] is False
    assert new_state["pawns"]["red"][0]["pos"] == 0
    assert new_state["dice"] is None


def test_trilha_initial_state():
    engine = TrilhaEngine()
    state = engine.get_initial_state()
    assert state["current_player"] == "white"
    assert state["phase"] == 1
    assert len(state["board"]) == 24


def test_trilha_place_piece():
    engine = TrilhaEngine()
    state = engine.get_initial_state()
    move = {"place": 0}
    assert engine.validate_move(state, move, "white") is True
    new_state = engine.apply_move(state, move)
    assert new_state["board"][0] == "white"
    assert new_state["players"]["white"]["pieces_in_hand"] == 8


def test_reversi_initial_state():
    engine = ReversiEngine()
    state = engine.get_initial_state()
    assert state["current_player"] == "black"
    assert state["board"][3][3] == "W"
    assert state["board"][3][4] == "B"


def test_reversi_black_move():
    engine = ReversiEngine()
    state = engine.get_initial_state()
    move = {"position": "e3"}
    assert engine.validate_move(state, move, "black") is True


def test_reversi_invalid_position():
    engine = ReversiEngine()
    state = engine.get_initial_state()
    move = {"position": "a1"}
    assert engine.validate_move(state, move, "black") is False


def test_reversi_apply_move():
    engine = ReversiEngine()
    state = engine.get_initial_state()
    move = {"position": "d3"}
    new_state = engine.apply_move(state, move)
    assert new_state["board"][5][3] == "B"
