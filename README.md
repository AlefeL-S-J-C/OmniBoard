# OmniBoard Engine

Motor para jogos de tabuleiro em tempo real com arquitetura pluggable: o núcleo não conhece as regras dos jogos diretamente — interage com uma máquina de estados abstrata, permitindo que Xadrez, Ludo ou Go funcionem sob a mesma infraestrutura.

## Funcionalidades

- **Arquitetura Baseada em Eventos:** Toda ação gera um evento imutável que altera o estado global da partida.
- **Validação no Servidor (Anti-Cheat):** O front-end é puramente visual — toda jogada é auditada pelo back-end.
- **Modo vs IA:** Jogue contra o computador em qualquer jogo suportado.
- **Seletor de Jogos:** Escolha entre 6 jogos diretamente na interface.
- **Ajuda Contextual:** Botão `?` que exibe regras e descrição das peças de cada jogo.
- **Botão Reiniciar:** Reinicia a partida atual sem recarregar a página.
- **Suporte Omnicanal:** WebSockets agnósticos prontos para Web (React) ou Mobile.

## Jogos Suportados

| Jogo | Tipo | Mecânicas Validadas pelo Servidor |
|------|------|-----------------------------------|
| **Xadrez** | Estratégia | Movimentação de todas as peças, xeque-mate, afogamento (empate) |
| **Dama** | Estratégia | Movimentação diagonal, captura obrigatória em cadeia, transformação em Damas, vitória por eliminação |
| **Go** | Estratégia | Colocação de pedras, captura por falta de liberdades, contagem de território, 2 passes consecutivos encerram |
| **Ludo** | Sorte | Dado seguro no servidor, saída com 6, captura, reta final (home stretch), 4 peões no centro vencem, rolagem automática da IA |
| **Trilha** | Estratégia | 3 fases (colocação/movimento/voo), formação de moinhos com captura |
| **Reversi** | Estratégia | Inversão em 8 direções, passe automático sem jogadas disponíveis |

## Arquitetura

```
[ Front-end (React + Vite) ]
       |  JSON via WebSocket (direto ws://localhost:8000)
[ FastAPI (Container) ]
       |
├── [ Matchmaking Pool ]  -- Redis (filas ELO)
├── [ GameManager ]       -- Valida e aplica jogadas
│   ├── [ AI Player ]     -- Jogadas automáticas (aleatórias)
│   └── [ Game Engine ]   -- Plugins (chess, checkers, go, ...)
└── [ Banco Híbrido ]
    ├── Redis              -- Estado quente (salas ativas)
    └── PostgreSQL         -- Histórico permanente (event sourcing)
```

## Estrutura

```
omniboard/
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── main.py                  # FastAPI, WebSocket, endpoints
│   ├── core/
│   │   ├── gateway.py           # Gerenciamento de conexões WebSocket
│   │   ├── lobby.py             # Matchmaking por ELO (Redis)
│   │   └── security.py          # JWT e bcrypt
│   ├── database/
│   │   ├── postgres.py          # SQLAlchemy assíncrono
│   │   └── redis_client.py      # Conexão Redis
│   └── games/
│       ├── base.py              # Classe abstrata BaseGame
│       ├── manager.py           # GameManager (estado + AI)
│       ├── ai.py                # Geradores de movimento por jogo
│       ├── chess.py / checkers.py / go.py
│       ├── ludo.py / trilha.py / reversi.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx / App.tsx
│       ├── index.css            # Tailwind v4
│       ├── hooks/useWebSocket.ts
│       ├── types/chess.ts
│       ├── utils/
│       │   ├── board.ts         # Parsing notação xadrez
│       │   ├── games.ts         # Info dos 6 jogos
│       │   └── auth.ts          # fetchDevToken
│       └── components/
│           ├── Board.tsx        # Dispatch para jogo específico
│           ├── Square.tsx       # Casa do tabuleiro
│           ├── LudoBoard.tsx    # Tabuleiro Ludo 15×15 com dado
│           ├── GoBoard.tsx      # Tabuleiro Go 9×9 com SVG (interseções)
│           ├── TrilhaBoard.tsx  # Tabuleiro Trilha em SVG
│           ├── GameInfo.tsx     # Turno atual e indicador de vencedor
│           ├── GameHelp.tsx     # Card de regras por jogo
│           ├── ConnectionStatus.tsx
│           └── DevLogin.tsx     # Login + seletor de jogo
└── tests/                       # Testes de jogadas
```

## Como Rodar

### Back-end (Docker)

```bash
docker compose up -d
```

### Front-end

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`, escolha o jogo e ative o modo IA para começar.

## API

### `POST /api/dev-login`

```json
{ "username": "jogador1", "game_type": "chess", "with_ai": true }
```

Retorna um token JWT para autenticação via WebSocket.

### `GET /api/games`

Lista os jogos disponíveis.

### `WebSocket /ws/{match_id}/{token}?game_type=chess&with_ai=true`

Conexão bidirecional direta (sem proxy). Eventos:

| Evento | Direção | Descrição |
|--------|---------|-----------|
| `conexao_estabelecida` | server → client | Estado inicial + cor do jogador |
| `movimento_confirmado` | server → client | Jogada validada + resposta da IA |
| `movimento_invalido` | server → client | Jogada rejeitada |
| `dice_rolled` | server → client | Resultado do dado (Ludo) |
| `partida_reiniciada` | server → client | Estado resetado ao inicial |
| `{ action: "move", payload: {from, to} }` | client → server | Envia jogada |
| `{ action: "roll_dice" }` | client → server | Rola o dado (Ludo) |
| `{ action: "restart" }` | client → server | Reinicia a partida |
