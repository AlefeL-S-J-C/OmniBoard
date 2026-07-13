from src.games.rules import GameRules, PieceType, MovePattern, CaptureRule, VictoryCondition

REVERSI_RULES = GameRules(
    game_type="reversi",
    name="Reversi / Othello",
    description="Jogo de inversão. Coloca peça cercando peças adversárias em 8 direções para virá-las. Mais peças no final vence.",
    board={"type": "grid", "size": 8, "coordinates": "algebraic"},
    players={"colors": ["black", "white"], "first_move": "black"},
    pieces={
        "black": [PieceType(symbol="●", name="Pedra Preta", color="black", flips=True)],
        "white": [PieceType(symbol="○", name="Pedra Branca", color="white", flips=True)],
    },
    move_patterns=[
        MovePattern(name="colocacao", description="Coloca peça em casa vazia que faz pelo menos uma inversão", pattern={"type": "place_with_flip", "directions": 8}),
        MovePattern(name="passar", description="Se não há jogada válida, passa a vez automaticamente", pattern={"type": "pass", "condition": "no_valid_moves"}),
    ],
    capture_rules=[
        CaptureRule(type="bracket_flip", description="Peças adversárias entre nova peça e peça própria são invertidas", directions=8, mandatory=True),
        CaptureRule(type="must_flip_at_least_one", description="Jogada só é válida se inverte pelo menos 1 peça", mandatory=True),
    ],
    special_rules=[
        {"name": "setup_inicial", "description": "4 peças centrais: diagonais iguais (e4/d5 brancas, d4/e5 pretas)", "fixed": True},
        {"name": "passar_obrigatorio", "description": "Sem jogadas válidas = passa automaticamente", "auto_pass": True},
        {"name": "duplo_pass_fim", "description": "Dois passes consecutivos = fim de jogo", "ends_game": True},
        {"name": "sem_captura_direta", "description": "Não há 'captura' tradicional, apenas inversão", "clarification": True},
        {"name": "paridade", "description": "Tabuleiro 8x8 = 64 casas, jogo sempre termina com tabuleiro cheio", "note": True},
    ],
    victory_conditions=[
        VictoryCondition(type="count_pieces", description="Mais peças da sua cor no tabuleiro = vence", details={"count_method": "total_on_board"}),
        VictoryCondition(type="early_resignation", description="Adversário desiste", details={"winner": "opponent"}),
        VictoryCondition(type="timeout", description="Tempo esgotado", details={"winner": "opponent_with_time"}),
        VictoryCondition(type="draw", description="Empate (32-32)", details={"result": "draw", "condition": "equal_pieces"}),
    ],
    ai_difficulty="medium",
)