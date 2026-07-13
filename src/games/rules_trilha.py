from src.games.rules import GameRules, PieceType, MovePattern, CaptureRule, PhaseRule, VictoryCondition

TRILHA_RULES = GameRules(
    game_type="trilha",
    name="Trilha (Nine Men's Morris)",
    description="Jogo milenar em 3 fases: colocação, movimento, voo. Forma moinhos (3 em linha) para capturar. Vence quem reduz adversário a <3 peças ou o bloqueia.",
    board={
        "type": "graph", "positions": 24, "connections": "concentric_squares",
        "mills": [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
            [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23],
            [0, 9, 21], [3, 10, 18], [6, 11, 15], [1, 4, 7],
            [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23],
        ],
    },
    players={"colors": ["white", "black"], "pieces_per_player": 9},
    pieces={
        "white": [PieceType(symbol="○", name="Peça Branca", color="white")],
        "black": [PieceType(symbol="●", name="Peça Preta", color="black")],
    },
    move_patterns=[
        MovePattern(name="colocacao", description="Fase 1: Coloca peça em qualquer posição vazia", pattern={"type": "place", "phase": 1}),
        MovePattern(name="movimento", description="Fase 2: Move peça para posição adjacente vazia", pattern={"type": "slide", "adjacent_only": True, "phase": 2}),
        MovePattern(name="voo", description="Fase 3: Com 3 peças, move para qualquer posição vazia", pattern={"type": "fly", "any_empty": True, "phase": 3, "condition": "pieces_on_board <= 3"}),
    ],
    capture_rules=[
        CaptureRule(type="mill_capture", description="Forma moinho (3 em linha) -> remove 1 peça adversária", mandatory=True, chain=False),
        CaptureRule(type="protected_mill", description="Não pode remover peça de moinho adversário (exceto se só restarem peças em moinho)", mandatory=True),
    ],
    phases=[
        PhaseRule(name="colocacao", description="Cada jogador coloca 9 peças alternadamente", transitions={"to_movement": "all_pieces_placed"}),
        PhaseRule(name="movimento", description="Move peças para posições adjacentes vazias", transitions={"to_flying": "pieces_on_board <= 3"}),
        PhaseRule(name="voo", description="Move qualquer peça para qualquer posição vazia", transitions={}),
    ],
    special_rules=[
        {"name": "moinho_duplo", "description": "Moinho formado com 1 peça completa 2 linhas = remove 2 peças", "double_capture": True},
        {"name": "remocao_obrigatoria", "description": "Ao formar moinho, deve remover peça se houver peça removível", "mandatory": True},
        {"name": "protecao_moinho", "description": "Peça em moinho não pode ser removida (a menos que todas estejam em moinho)", "protection": True},
        {"name": "vitoria_antecipada", "description": "Adversário fica com 2 peças = vitória imediata", "early_win": True},
    ],
    victory_conditions=[
        VictoryCondition(type="piece_reduction", description="Adversário reduzido a 2 peças no tabuleiro", details={"winner": "player_with_more_pieces"}),
        VictoryCondition(type="blockade", description="Adversário sem movimentos legais (bloqueado)", details={"winner": "player_with_moves"}),
        VictoryCondition(type="resignation", description="Adversário desiste", details={"winner": "opponent"}),
        VictoryCondition(type="timeout", description="Tempo esgotado", details={"winner": "opponent_with_time"}),
        VictoryCondition(type="draw_agreement", description="Empate acordado", details={"result": "draw"}),
        VictoryCondition(type="draw_repetition", description="Repetição de posição", details={"result": "draw"}),
    ],
    ai_difficulty="medium",
)