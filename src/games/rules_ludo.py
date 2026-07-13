from src.games.rules import GameRules, PieceType, MovePattern, CaptureRule, PhaseRule, VictoryCondition

LUDO_RULES = GameRules(
    game_type="ludo",
    name="Ludo",
    description="Jogo de corrida com dados para 4 jogadores. Peças saem da base com 6, avançam pelo tabuleiro, capturam adversários e entram na reta final. Vence quem levar 4 peões ao centro primeiro.",
    board={
        "type": "cross_track",
        "track_length": 56,
        "home_stretch": 6,
        "start_positions": 4,
        "colors": ["red", "green", "yellow", "blue"],
        "safe_squares": [0, 8, 13, 21, 26, 34, 39, 47, 52],
    },
    players={"colors": ["red", "green", "yellow", "blue"], "pieces_per_player": 4, "min_players": 2, "max_players": 4},
    pieces={
        "red": [PieceType(symbol="R", name="Peão Vermelho", color="red")],
        "green": [PieceType(symbol="G", name="Peão Verde", color="green")],
        "yellow": [PieceType(symbol="Y", name="Peão Amarelo", color="yellow")],
        "blue": [PieceType(symbol="B", name="Peão Azul", color="blue")],
    },
    move_patterns=[
        MovePattern(name="saida_base", description="Sai da base para casa inicial com dado 6", pattern={"type": "exit_base", "condition": "dice == 6"}),
        MovePattern(name="avanco", description="Avança número de casas igual ao dado", pattern={"type": "advance", "distance": "dice_value"}),
        MovePattern(name="entrada_reta_final", description="Entra na reta final com número exato", pattern={"type": "enter_home_stretch", "exact": True}),
        MovePattern(name="centro", description="Chega ao centro com número exato na reta final", pattern={"type": "reach_center", "exact": True}),
        MovePattern(name="seis_extra", description="Tirar 6 dá jogada extra", pattern={"type": "extra_turn", "condition": "dice == 6"}),
    ],
    capture_rules=[
        CaptureRule(type="capture", description="Cai em casa com peça adversária (exceto casas seguras) -> adversário volta à base", mandatory=False),
        CaptureRule(type="safe_square", description="Casas seguras (iniciais e marcadas) não permitem captura", protection=True),
        CaptureRule(type="stack_own", description="Pode empilhar próprias peças na mesma casa", stacking=True),
    ],
    phases=[
        PhaseRule(name="base", description="Peças na base, aguardam 6 para sair"),
        PhaseRule(name="track", description="Peças no tabuleiro principal, avançam pelo caminho"),
        PhaseRule(name="home_stretch", description="Reta final colorida de 6 casas"),
        PhaseRule(name="center", description="Centro do tabuleiro = vitória do peão"),
    ],
    special_rules=[
        {"name": "dado_6", "description": "Tirar 6: sai da base OU joga extra", "effects": ["exit_base", "extra_turn"]},
        {"name": "tres_seis", "description": "Três 6 seguidos = perde a vez (regra opcional)", "penalty": "lose_turn"},
        {"name": "captura_volta_base", "description": "Peça capturada retorna à base, precisa de 6 para sair de novo", "reset": True},
        {"name": "casa_segura", "description": "8 casas seguras + 4 iniciais = 12 casas onde não pode capturar", "positions": [0, 8, 13, 21, 26, 34, 39, 47, 52]},
        {"name": "bloco", "description": "2+ peças próprias na mesma casa formam bloco (não pode ser passado por adversário em algumas variantes)", "blocking": True},
        {"name": "vitoria_4_peoes", "description": "Primeiro a colocar 4 peões no centro vence", "condition": "pieces_in_center == 4"},
    ],
    victory_conditions=[
        VictoryCondition(type="all_home", description="Primeiro a levar 4 peões ao centro vence", details={"winner": "first_to_4_in_center"}),
        VictoryCondition(type="timeout", description="Tempo esgotado", details={"winner": "opponent_with_time"}),
        VictoryCondition(type="resignation", description="Adversário desiste", details={"winner": "opponent"}),
    ],
    ai_difficulty="easy",
)