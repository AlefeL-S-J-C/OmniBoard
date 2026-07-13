from src.games.rules import GameRules, PieceType, MovePattern, CaptureRule, VictoryCondition

CHECKERS_RULES = GameRules(
    game_type="checkers",
    name="Dama (Checkers - Regras Brasileiras/Internacionais)",
    description="Jogo diagonal. Captura obrigatória, peão vira dama na última fileira, dama move múltiplas casas.",
    board={"type": "grid", "size": 8, "playable_squares": "dark_only", "coordinates": "algebraic"},
    players={"colors": ["white", "black"], "first_move": "white"},
    pieces={
        "white": [
            PieceType(symbol="○", name="Peão Branco", color="white", moves="diagonal_forward_1", captures="diagonal_forward_1", promotes_to="Dama Branca"),
            PieceType(symbol="●", name="Dama Branca", color="white", moves="diagonal_unlimited", captures="diagonal_unlimited", promoted=True),
        ],
        "black": [
            PieceType(symbol="○", name="Peão Preto", color="black", moves="diagonal_forward_1", captures="diagonal_forward_1", promotes_to="Dama Preta"),
            PieceType(symbol="●", name="Dama Preta", color="black", moves="diagonal_unlimited", captures="diagonal_unlimited", promoted=True),
        ],
    },
    move_patterns=[
        MovePattern(name="peao_move", description="Peão move 1 casa diagonal frente", pattern={"type": "diagonal_step", "forward_only": True, "distance": 1}),
        MovePattern(name="dama_move", description="Dama move qualquer distância diagonal", pattern={"type": "diagonal_slide", "unlimited": True}),
        MovePattern(name="peao_capture", description="Peão captura pulando 1 casa diagonal", pattern={"type": "diagonal_jump", "distance": 2, "capture_mid": True}),
        MovePattern(name="dama_capture", description="Dama captura pulando qualquer distância", pattern={"type": "diagonal_slide_jump", "unlimited": True, "capture_mid": True}),
        MovePattern(name="multi_capture", description="Capturas em cadeia obrigatórias", pattern={"type": "multi_jump", "mandatory": True, "must_maximize": True}),
    ],
    capture_rules=[
        CaptureRule(type="mandatory_capture", description="Se há captura possível, deve capturar", mandatory=True),
        CaptureRule(type="maximize_capture", description="Deve escolher sequência que captura mais peças (regras brasileiras)", mandatory=True),
        CaptureRule(type="king_capture_priority", description="Dama não tem prioridade sobre peão na captura (regras brasileiras)", mandatory=False),
        CaptureRule(type="no_back_capture_pawn", description="Peão não captura para trás (regras brasileiras)", mandatory=True),
    ],
    special_rules=[
        {"name": "promocao", "description": "Peão na última fileira vira Dama", "mandatory": True, "immediate": True},
        {"name": "promocao_meio_captura", "description": "Peão vira Dama no meio de captura múltipla e continua capturando como Dama", "continues_as_king": True},
        {"name": "captura_obrigatoria", "description": "Não pode fazer movimento simples se existe captura", "mandatory": True},
        {"name": "dama_move_livre", "description": "Dama move/captura qualquer distância diagonal", "unlimited_range": True},
    ],
    victory_conditions=[
        VictoryCondition(type="elimination", description="Capturar todas as peças adversárias", details={"winner": "player_with_pieces"}),
        VictoryCondition(type="blockade", description="Adversário sem movimentos legais", details={"winner": "player_with_moves"}),
        VictoryCondition(type="resignation", description="Adversário desiste", details={"winner": "opponent"}),
        VictoryCondition(type="draw_agreement", description="Empate acordado", details={"result": "draw"}),
        VictoryCondition(type="draw_25_moves", description="25 lances de dama sem captura ou movimento de peão = empate (opcional)", details={"result": "draw"}),
        VictoryCondition(type="threefold_repetition", description="Repetição tripla de posição = empate", details={"result": "draw"}),
    ],
    ai_difficulty="medium",
)