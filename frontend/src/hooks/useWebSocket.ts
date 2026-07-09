import { useCallback, useEffect, useRef, useState } from "react";
import type { GameState, Move } from "../types/chess";

interface UseWebSocketOptions {
  matchId: string;
  playerToken: string;
  gameType?: string;
  withAi?: boolean;
}

type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export function useWebSocket({
  matchId,
  playerToken,
  gameType = "chess",
  withAi = true,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [playerColor, setPlayerColor] = useState<"white" | "black">("white");
  const [currentGameType, setCurrentGameType] = useState(gameType);
  const [aiMove, setAiMove] = useState<Move | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!matchId || !playerToken) return;

    setStatus("connecting");
    setError(null);

    const wsUrl = new URL(`ws://${import.meta.env.VITE_WS_URL}/ws/${matchId}/${playerToken}`, "http://example.com");
    const url = `${wsUrl}?game_type=${gameType}&with_ai=${withAi}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setStatus("connected");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.evento === "conexao_estabelecida") {
          if (data.sua_cor) setPlayerColor(data.sua_cor as "white" | "black");
          if (data.novo_estado) setGameState(data.novo_estado as GameState);
          if (data.game_type) setCurrentGameType(data.game_type as string);
        }

        if (data.evento === "movimento_confirmado") {
          if (data.novo_estado) setGameState(data.novo_estado as GameState);
          if (data.ai_move) setAiMove(data.ai_move as Move);
        }

        if (data.evento === "dice_rolled") {
          if (data.novo_estado) setGameState(data.novo_estado as GameState);
        }

        if (data.evento === "partida_reiniciada") {
          if (data.novo_estado) setGameState(data.novo_estado as GameState);
          setError(null);
        }

        if (data.evento === "movimento_invalido") {
          setError(data.message ?? "Jogada inválida");
        }
      } catch {
        setError("Falha ao processar mensagem do servidor");
      }
    };

    ws.onerror = () => {
      setStatus("error");
      setError("Erro de conexão com o servidor");
    };

    ws.onclose = () => {
      setStatus("disconnected");
      wsRef.current = null;
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [matchId, playerToken, gameType, withAi]);

  const sendMove = useCallback(
    (payload: Record<string, unknown>) => {
      setError(null);
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "move", payload }));
      }
  },
  []);

  const rollDice = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "roll_dice" }));
    }
  }, []);

  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return {
    status,
    gameState,
    playerColor,
    currentGameType,
    aiMove,
    error,
    sendMove,
    rollDice,
    sendMessage,
  };
}