import { useCallback, useEffect, useState } from "react";
import confetti from "canvas-confetti";
import Board from "./components/Board";
import ConnectionStatus from "./components/ConnectionStatus";
import DevLogin from "./components/DevLogin";
import GameHelp from "./components/GameHelp";
import GameInfo from "./components/GameInfo";
import { useWebSocket } from "./hooks/useWebSocket";
import { GAMES } from "./utils/games";

interface Session {
  matchId: string;
  playerToken: string;
  username: string;
  gameType: string;
  withAi: boolean;
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null);

  const {
    status,
    gameState,
    playerColor,
    currentGameType,
    error,
    sendMove,
    rollDice,
    sendMessage,
  } = useWebSocket({
    matchId: session?.matchId ?? "",
    playerToken: session?.playerToken ?? "",
    gameType: session?.gameType ?? "chess",
    withAi: session?.withAi ?? true,
  });

  const winner = gameState?.vencedor as string | undefined;

  useEffect(() => {
    if (winner) {
      confetti({
        particleCount: 200,
        spread: 100,
        origin: { y: 0.6 },
        colors: ["#f59e0b", "#ef4444", "#22c55e", "#3b82f6", "#a855f7"],
      });
    }
  }, [winner]);

  const handleLogin = useCallback(
    (
      matchId: string,
      playerToken: string,
      username: string,
      gameType: string,
      withAi: boolean
    ) => {
      setSession({ matchId: `${gameType}_${matchId}`, playerToken, username, gameType, withAi });
    },
    []
  );

  const handleMove = useCallback(
    (move: Record<string, unknown>) => {
      sendMove(move as Record<string, unknown>);
    },
    [sendMove]
  );

  const handleRestart = useCallback(() => {
    sendMessage({ action: "restart" });
  }, [sendMessage]);

  const handleBackToMenu = useCallback(() => {
    setSession(null);
  }, []);

  if (!session) {
    return <DevLogin onLogin={handleLogin} />;
  }

  const boardState = gameState ?? null;
  const gameName = GAMES.find((g) => g.id === currentGameType)?.name ?? currentGameType;

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-900 text-white p-4">
      <header className="flex items-center justify-between w-full max-w-[640px] mb-4">
        <div>
          <h1 className="text-2xl font-bold">OmniBoard</h1>
          <p className="text-sm text-gray-400 capitalize">{gameName}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleBackToMenu}
            className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            Menu
          </button>
          <button
            onClick={handleRestart}
            className="px-3 py-1 text-sm bg-red-700 hover:bg-red-600 rounded transition-colors"
          >
            Reiniciar
          </button>
          <ConnectionStatus status={status} error={error} />
        </div>
      </header>

      <GameInfo gameState={boardState} playerColor={playerColor} />

      {boardState ? (
        <Board
          gameState={boardState}
          onMove={handleMove}
          onRollDice={rollDice}
          playerColor={playerColor}
          gameType={currentGameType}
        />
      ) : (
        <div className="flex items-center justify-center w-full max-w-[640px] aspect-square bg-gray-800 border-4 border-amber-900 rounded-lg">
          <div className="text-center text-gray-400">
            <p className="text-6xl mb-4">&#9820;</p>
            <p className="text-lg">
              {status === "connecting"
                ? "Conectando ao servidor..."
                : "Aguardando estado do tabuleiro..."}
            </p>
          </div>
        </div>
      )}

      <div className="mt-6 flex gap-4 text-sm text-gray-500">
        <span>Partida: {session.matchId}</span>
        <span>Jogador: {session.username}</span>
        {session.withAi && <span>vs IA</span>}
      </div>

      <GameHelp gameType={currentGameType} />
    </div>
  );
}
