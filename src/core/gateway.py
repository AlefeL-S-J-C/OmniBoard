from fastapi import WebSocket

from src.core.security import decode_token

COLORS = ["white", "black"]


class GatewayManager:
    def __init__(self):
        self._connections: dict[str, dict[int, WebSocket]] = {}
        self._player_colors: dict[str, dict[int, str]] = {}

    async def authenticate(self, token: str) -> dict | None:
        payload = decode_token(token)
        return payload

    async def connect(self, ws: WebSocket, match_id: str, player_id: int):
        await ws.accept()
        self._connections.setdefault(match_id, {})[player_id] = ws
        colors = self._player_colors.setdefault(match_id, {})
        if player_id not in colors:
            taken = set(colors.values())
            for color in COLORS:
                if color not in taken:
                    colors[player_id] = color
                    break

    async def disconnect(self, match_id: str, player_id: int):
        self._connections.get(match_id, {}).pop(player_id, None)
        self._player_colors.get(match_id, {}).pop(player_id, None)

    def get_player_color(self, match_id: str, player_id: int) -> str:
        return self._player_colors.get(match_id, {}).get(player_id, "white")

    async def broadcast(self, match_id: str, message: dict, exclude: int | None = None):
        for pid, ws in self._connections.get(match_id, {}).items():
            if pid != exclude:
                await ws.send_json(message)

    async def send_to(self, match_id: str, player_id: int, message: dict):
        ws = self._connections.get(match_id, {}).get(player_id)
        if ws:
            await ws.send_json(message)

    async def handle_message(
        self, match_id: str, player_id: int, data: dict, game_manager=None
    ):
        action = data.get("action")
        if action == "roll_dice" and game_manager:
            player_color = self.get_player_color(match_id, player_id)
            result = game_manager.roll_dice(match_id, player_color)
            if result:
                new_state, dice = result
                await self.broadcast(match_id, {
                    "evento": "dice_rolled",
                    "novo_estado": new_state,
                    "dice": dice,
                    "jogador": player_id,
                })
            else:
                await self.send_to(match_id, player_id, {
                    "evento": "movimento_invalido",
                    "message": "Não é sua vez ou dado já foi rolado",
                })
        elif action == "restart" and game_manager:
            new_state = game_manager.restart_match(match_id)
            if new_state:
                await self.broadcast(match_id, {
                    "evento": "partida_reiniciada",
                    "novo_estado": new_state,
                    "message": "Partida reiniciada!",
                })
        elif action == "move" and game_manager:
            payload = data.get("payload", {})
            player_color = self.get_player_color(match_id, player_id)
            valid, new_state, winner, ai_move = game_manager.process_move(
                match_id, payload, player_color
            )
            if valid:
                event: dict = {
                    "evento": "movimento_confirmado",
                    "novo_estado": new_state,
                    "jogador": player_id,
                }
                if winner:
                    event["vencedor"] = winner
                if ai_move:
                    event["ai_move"] = ai_move
                await self.broadcast(match_id, event)
            else:
                await self.send_to(
                    match_id,
                    player_id,
                    {
                        "evento": "movimento_invalido",
                        "message": winner or "Jogada inválida",
                    },
                )
        else:
            await self.broadcast(match_id, data, exclude=player_id)
