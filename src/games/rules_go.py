from src.games.rules import GameRules, PieceType, MovePattern, CaptureRule, VictoryCondition

GO_RULES = GameRules(
    game_type="go",
    name="Go (Baduk/Weiqi)",
    description="Jogo de territórios. Coloca pedras para cercar área e capturar pedras adversárias sem liberdades.",
    board={"type": "grid", "size": 9, "coordinates": "alphanumeric"},
    players={"colors": ["black", "white"], "handicap": "optional"},
    pieces={
        "black": [PieceType(symbol="●", name="Pedra Preta", color="black")],
        "white": [PieceType(symbol="○", name="Pedra Branca", color="white")],
    },
    move_patterns=[
        MovePattern(name="colocacao", description="Coloca pedra em interseção vazia", pattern={"type": "place", "empty_only": True}),
        MovePattern(name="passar", description="Passa a vez (sem colocar pedra)", pattern={"type": "pass"}),
    ],
    capture_rules=[
        CaptureRule(type="liberty_capture", description="Grupo sem liberdades (espaços vazios adjacentes) é capturado", mandatory=True),
        CaptureRule(type="ko_rule", description="Ko: não pode repetir posição anterior imediata", mandatory=True),
        CaptureRule(type="suicide_prohibited", description="Jogada suicida (sem capturar) proibida", mandatory=True),
    ],
    special_rules=[
        {"name": "ko", "description": "Proíbe recaptura imediata de pedra única", "tracks_position": True},
        {"name": "komi", "description": "Compensação para Branco (geralmente 6.5 pontos)", "value": 6.5, "applies_to": "white"},
        {"name": "handicap", "description": "Pedras iniciais para equilibrar níveis", "optional": True, "positions": "star_points"},
        {"name": "two_passes_end", "description": "Dois passes consecutivos encerram a partida", "mandatory": True},
        {"name": "scoring", "description": "Área (território + pedras) ou território (apenas espaços vazios cercados)", "method": "area_or_territory"},
    ],
    victory_conditions=[
        VictoryCondition(type="territory_scoring", description="Mais território + capturas + komi vence", details={"method": "area_or_territory"}),
        VictoryCondition(type="resignation", description="Adversário desiste", details={"winner": "opponent"}),
        VictoryCondition(type="timeout", description="Tempo esgotado", details={"winner": "opponent_with_time"}),
        VictoryCondition(type="draw", description="Empate (jigo) se pontuação igual", details={"possible": True}),
    ],
    ai_difficulty="medium",
)