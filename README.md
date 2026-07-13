# OmniBoard Engine

Motor para jogos de tabuleiro em tempo real com arquitetura pluggable: o núcleo **conhece todas as regras de todos os jogos** via *Rules Registry* declarativo — interage com engines abstratas, permitindo que Xadrez, Dama, Go, Ludo, Trilha ou Reversi funcionem sob a mesma infraestrutura.

---

## Funcionalidades

- **Arquitetura Baseada em Eventos** – Toda ação gera um evento imutável que altera o estado global da partida.
- **Validação no Servidor (Anti‑Cheat)** – O front‑end é puramente visual; toda jogada é auditada pelo back‑end.
- **Modo vs IA** – Jogue contra o computador em qualquer jogo suportado.
- **Matchmaking PvP (ELO)** – Fila por tipo de jogo, emparelhamento automático e criação de partida.
- **Autenticação Completa** – Registro/login com e‑mail/senha (bcrypt + JWT) + placeholders para OAuth (Google, GitHub).
- **Push Notifications** – Suporte a FCM (Android/Web) e APNs (iOS) para avisar “sua vez”.
- **Replay / Histórico** – Event‑sourcing no PostgreSQL; endpoint `GET /api/matches/{id}/events` reconstrói a partida lance a lance.
- **Espectador (Read‑Only WS)** – Conexão `ws://…/ws/watch/{match_id}` para assistir sem jogar.
- **Seletor de Jogos** – Escolha entre 6 jogos diretamente na interface.
- **Ajuda Contextual** – Botão `?` que exibe regras e descrição das peças de cada jogo.
- **Botão Reiniciar** – Reinicia a partida atual sem recarregar a página.
- **Suporte Omnicanal** – WebSockets agnósticos prontos para Web (React) ou Mobile.
- **Observabilidade** – OpenTelemetry → Tempo (traces) + Prometheus (`/metrics`).
- **Internacionalização (i18n)** – pt‑BR e EN (detector de idioma + `localStorage`).

---

## Jogos Suportados

| Jogo   | Tipo      | Mecânicas Validadas pelo Servidor |
|--------|-----------|-----------------------------------|
| **Xadrez**   | Estratégia | Movimentação de todas as peças, xeque‑mate, afogamento (empate) |
| **Dama**     | Estratégia | Movimentação diagonal, captura obrigatória em cadeia, transformação em Damas, vitória por eliminação |
| **Go**       | Estratégia | Colocação de pedras, captura por falta de liberdades, contagem de território, 2 passes consecutivos encerram |
| **Ludo**     | Sorte      | Dado seguro no servidor, saída com 6, captura, reta final (home stretch), 4 peões no centro vencem, rolagem automática da IA |
| **Trilha**   | Estratégia | 3 fases (colocação/movimento/voo), formação de moinhos com captura |
| **Reversi**  | Estratégia | Inversão em 8 direções, passe automático sem jogadas disponíveis |

---

## Arquitetura

```
[ Front‑end (React 19 + Vite + Tailwind v4 + TS) ]
        │  JSON via WebSocket (ws://host/ws/…)
[ FastAPI (Container) ]
        │
├── [ Matchmaking Pool ]   -- Redis (filas ELO)
├── [ GameManager ]        -- Valida e aplica jogadas
│   ├── [ AI Player ]      -- Movimentos aleatórios válidos (plugável)
│   ├── [ Game Engine ]    -- Plugins (chess, checkers, go, ludo, trilha, reversi)
│   └── [ Rules Registry ] -- **Regras declarativas de todos os jogos** (novo)
└── [ Banco Híbrido ]
    ├── Redis               -- Estado quente (salas ativas)
    └── PostgreSQL          -- Histórico permanente (event sourcing)
```

---

## Estrutura de Pastas

```
omniboard/
├── docker-compose.yml                # dev (hot‑reload)
├── docker-compose.prod.yml           # prod (Caddy + TLS + Tempo + Prometheus)
├── Caddyfile                         # reverse-proxy + HTTPS automático (produção)
├── Caddyfile.dev                     # reverse-proxy para desenvolvimento local (localhost)
├── Dockerfile                        # multi-stage Python
├── requirements.txt
├── pytest.ini
├── alembic.ini                       # configuração Alembic (migrações)
├── .github/workflows/ci.yml          # lint, type-check, test, build
├── src/
│   ├── main.py                       # FastAPI, WS, rotas HTTP
│   ├── core/
│   │   ├── gateway.py                # Gerenciamento de conexões WS
│   │   ├── lobby.py                  # Matchmaking (Redis + ELO)
│   │   ├── security.py               # JWT + bcrypt
│   │   └── observability.py          # OpenTelemetry + Prometheus (opcional em dev)
│   ├── database/
│   │   ├── postgres.py               # SQLAlchemy assíncrono + modelos
│   │   ├── redis_client.py
│   │   └── models.py                 # User, Match, MatchEvent
│   ├── games/
│   │   ├── base.py
│   │   ├── manager.py
│   │   ├── ai.py
│   │   ├── rules.py                  # **Rules Registry (novo)**
│   │   ├── rules_chess.py            # **Regras declarativas do Xadrez (novo)**
│   │   ├── rules_checkers.py         # **Regras declarativas da Dama (novo)**
│   │   ├── rules_go.py               # **Regras declarativas do Go (novo)**
│   │   ├── rules_ludo.py             # **Regras declarativas do Ludo (novo)**
│   │   ├── rules_reversi.py          # **Regras declarativas do Reversi (novo)**
│   │   ├── rules_trilha.py           # **Regras declarativas da Trilha (novo)**
│   │   ├── chess.py / checkers.py / go.py
│   │   ├── ludo.py / trilha.py / reversi.py
│   │   └── push/
│   │       └── service.py            # FCM / APNs
│   └── auth/
│       └── oauth.py                  # Google / GitHub placeholders
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example                  # exemplo de variáveis frontend
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── i18n.ts
│       ├── locales/pt-BR.json, en-US.json
│       ├── hooks/useWebSocket.ts
│       ├── utils/{auth,games,board}.ts
│       └── components/
│           ├── Board.tsx / ChessBoard.tsx / LudoBoard.tsx …
│           ├── AuthScreen.tsx
│           ├── MatchmakingScreen.tsx
│           ├── ReplayPanel.tsx
│           ├── GameInfo.tsx / GameHelp.tsx / ConnectionStatus.tsx
├── alembic/                          # migrações de banco (Alembic)
│   ├── env.py
│   └── versions/
└── tests/
    └── test_games.py + test_integration.py
```

---

## Como Rodar

### Pré‑requisitos

- **Docker Desktop** (backend + PostgreSQL + Redis)
- **Node.js 18+** (frontend)
- **Python 3.11+** (opcional, para rodar testes localmente)

---

### 1️⃣  Variáveis de Ambiente

```bash
cp .env.example .env
# Edite .env com suas chaves:
#   POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
#   POSTGRES_HOST=localhost, POSTGRES_PORT=5432    # ou db:5432 no Docker
#   REDIS_HOST=localhost, REDIS_PORT=6379           # ou redis:6379 no Docker
#   JWT_SECRET (>=32 chars)
#   GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REDIRECT_URI
#   GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET / GITHUB_REDIRECT_URI
#   FIREBASE_SERVICE_ACCOUNT_JSON (caminho do arquivo ou JSON inline)
#   OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317   # opcional (produção com Tempo)
#   LOG_LEVEL=INFO
```

Frontend (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=localhost:8000
```

Copie de `frontend/.env.example`.

---

### 2️⃣  Desenvolvimento (hot‑reload)

```bash
# sobe Postgres, Redis e API com reload + roda migrações (alembic upgrade head)
docker compose up -d

# front‑end
cd frontend
npm ci
npm run dev          # http://localhost:5173
```

A API fica em `http://localhost:8000` (Swagger em `/docs`).

---

### 3️⃣  Produção (HTTPS automático via Caddy)

```bash
# 1. Configure seu domínio no Caddyfile (substitua omniboard.example.com)
# 2. Certifique-se de que o domínio aponta para o IP do host
# 3. Suba a stack (roda migrações + build das imagens)
docker compose -f docker-compose.prod.yml up -d --build
```

Caddy obtém/renova certificados Let's Encrypt automaticamente.  
Serviços expostos:

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **Frontend** | 80/443 | Arquivos estáticos (nginx) |
| **API / WS** | 80/443 | Proxied pelo Caddy (`/api/*`, `/ws/*`) |
| **Prometheus** | 9090 | Métricas (`/metrics`) |
| **Tempo** | 3200 | Traces OpenTelemetry |

---

## API – Resumo

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/auth/register` | Cria usuário (username, email, password) → retorna JWT |
| `POST` | `/api/auth/login` | Login → retorna JWT |
| `GET`  | `/api/auth/oauth/{provider}` | Inicia fluxo OAuth (google | github) |
| `POST` | `/api/auth/oauth/{provider}/callback` | Recebe `code`, troca por token, devolve JWT |
| `GET`  | `/api/games` | Lista jogos disponíveis |
| `GET`  | `/api/games/rules` | **Lista todos os jogos com regras completas (novo)** |
| `GET`  | `/api/games/rules/{game_type}` | **Retorna regras declarativas de um jogo (novo)** |
| `POST` | `/api/matchmaking/join` | Entra na fila (`game_type`, `with_ai`) → `{matched, match_id}` |
| `POST` | `/api/matchmaking/leave` | Sai da fila |
| `GET`  | `/api/matches/{id}/events?turn=` | Histórico de lances (replay) |
| `PUT`  | `/api/users/me/fcm` | Salva token FCM/APNs para push |
| `WS`   | `/ws/{match_id}/{player_token}?game_type=…&with_ai=…` | Jogador (ações: `move`, `roll_dice`, `restart`) |
| `WS`   | `/ws/watch/{match_id}?token=` | Espectador (read‑only) |
| `GET`  | `/health` | Health‑check |
| `GET`  | `/metrics` | Prometheus metrics |

**Exemplo de payload WS (move – xadrez)**  

```json
{ "action": "move", "payload": { "from": "e2", "to": "e4" } }
```

**Evento de resposta**  

```json
{
  "evento": "movimento_confirmado",
  "novo_estado": { … },
  "jogador": 12,
  "ai_move": { "from": "e7", "to": "e5" }   // opcional
}
```

---

## Testes

```bash
# Backend (precisa de Postgres/Redis rodando – docker compose up -d)
docker compose exec web python -m pytest -q

# Frontend (type‑check)
cd frontend && npx tsc --noEmit
```

Integração (HTTP + WS) em `tests/test_integration.py`.

---

## Deploy Checklist

- [ ] Domínio configurado no `Caddyfile` (`seu-dominio.com`).
- [ ] Secrets (`JWT_SECRET`, `POSTGRES_PASSWORD`, OAuth keys, Firebase) no `.env` do servidor / GitHub Actions.
- [ ] Migrações Alembic aplicadas (`alembic upgrade head` – roda automaticamente no `docker compose up`).
- [ ] `docker compose -f docker-compose.prod.yml up -d --build` saúde OK (`/health`, `/metrics`).
- [ ] Push notifications testadas (FCM token salvo, `/api/users/me/fcm`).
- [ ] Alertas Prometheus/Grafana (latência, erro 5xx, fila de matchmaking).

---

## Desenvolvimento – Adicionar Novo Jogo

1. Crie `src/games/novo_jogo.py` herdando `BaseGame`.
2. Implemente `get_initial_state`, `validate_move`, `apply_move`, `check_victory`.
3. Registre em `src/games/manager.py` no dict `ENGINES`.
4. **Crie `src/games/rules_novo_jogo.py` com `GameRules` declarativo** (peças, movimentos, capturas, vitórias, fases).
5. Registre as regras em `src/games/rules.py` na função `load_all_rules`.
6. (Opcional) Adicione gerador de movimentos em `src/games/ai.py`.
7. Front‑end: crie `NovoJogoBoard.tsx` e adicione em `Board.tsx` + `utils/games.ts`.
8. Traduza textos nos arquivos `frontend/src/locales/*.json`.

---

## Comandos Úteis

```bash
# Backend
docker compose up -d --build      # rebuild & sobe
docker compose down -v            # para e remove volumes (limpa BD)
docker compose exec web bash      # shell no container

# Migrações (Alembic)
docker compose exec web alembic revision --autogenerate -m "mensagem"
docker compose exec web alembic upgrade head
docker compose exec web alembic downgrade -1

# Frontend
cd frontend
npm run build                     # build produção (pasta dist/)
npx tsc --noEmit                  # type check
npm run preview                   # preview do build

# Testes
python -m pytest tests/ -v --tb=short
```

---

## Status do Projeto (Jul 2026)

- ✅ 6 jogos implementados e testados (25 testes unitários)
- ✅ **Rules Registry declarativo — o núcleo conhece todas as regras** (novo)
- ✅ Backend FastAPI + WebSocket + JWT + bcrypt
- ✅ Frontend React 19 + Vite + Tailwind v4 + TypeScript
- ✅ Docker Compose (dev + prod) com Postgres, Redis, Caddy, Tempo, Prometheus
- ✅ Matchmaking ELO funcional
- ✅ Persistência completa (event‑sourcing) + replay
- ✅ Push notifications (FCM / APNs)
- ✅ Testes de integração (HTTP + WS)
- ✅ Observabilidade (traces + métricas)
- ✅ i18n pt‑BR / EN
- ✅ Migrações de banco com Alembic
- ✅ Configuração por ambiente (.env + .env.example)
- 🔄 OAuth Google / GitHub (endpoints prontos, faltam credenciais)
- 🔄 CI/CD (GitHub Actions) – build & push imagem

---

## Licença

MIT – sinta‑se livre para usar, modificar e distribuir. 🎉