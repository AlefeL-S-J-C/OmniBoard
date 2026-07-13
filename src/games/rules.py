from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


class PieceType(BaseModel):
    symbol: str
    name: str
    color: str


class MovePattern(BaseModel):
    name: str
    description: str
    pattern: dict[str, Any]


class CaptureRule(BaseModel):
    type: str
    description: str
    mandatory: bool = False
    chain: bool = False


class PhaseRule(BaseModel):
    name: str
    description: str
    transitions: dict[str, str] = field(default_factory=dict)


class VictoryCondition(BaseModel):
    type: str
    description: str
    details: dict[str, Any] = field(default_factory=dict)


class GameRules(BaseModel):
    game_type: str
    name: str
    description: str
    board: dict[str, Any]
    players: dict[str, Any]
    pieces: dict[str, list[PieceType]]
    move_patterns: list[MovePattern]
    capture_rules: list[CaptureRule]
    special_rules: list[dict[str, Any]] = field(default_factory=list)
    phases: list[PhaseRule] | None = None
    victory_conditions: list[VictoryCondition]
    ai_difficulty: str = "easy"


@dataclass
class RulesRegistry:
    _rules: dict[str, GameRules] = field(default_factory=dict, init=False)

    def register(self, rules: GameRules) -> None:
        self._rules[rules.game_type] = rules

    def get(self, game_type: str) -> GameRules | None:
        return self._rules.get(game_type)

    def list(self) -> list[str]:
        return list(self._rules.keys())

    def validate_move_format(self, game_type: str, move: dict) -> tuple[bool, str | None]:
        rules = self.get(game_type)
        if not rules:
            return False, f"Jogo desconhecido: {game_type}"
        return True, None

    def get_piece_moves(self, game_type: str, piece: str) -> list[MovePattern]:
        rules = self.get(game_type)
        if not rules:
            return []
        return [p for p in rules.move_patterns if p.name.lower() == piece.lower()]

    def get_victory_conditions(self, game_type: str) -> list[VictoryCondition]:
        rules = self.get(game_type)
        return rules.victory_conditions if rules else []

    def get_game_info(self, game_type: str) -> dict | None:
        rules = self.get(game_type)
        if not rules:
            return None
        return rules.model_dump()


def load_all_rules(registry: RulesRegistry) -> None:
    from src.games.rules_chess import CHESS_RULES
    from src.games.rules_checkers import CHECKERS_RULES
    from src.games.rules_go import GO_RULES
    from src.games.rules_ludo import LUDO_RULES
    from src.games.rules_reversi import REVERSI_RULES
    from src.games.rules_trilha import TRILHA_RULES

    for rules in [CHESS_RULES, CHECKERS_RULES, GO_RULES, LUDO_RULES, REVERSI_RULES, TRILHA_RULES]:
        registry.register(rules)