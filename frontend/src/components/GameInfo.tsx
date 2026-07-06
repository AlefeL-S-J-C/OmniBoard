import { LUDO_COLORS, PLAYER_NAMES } from "../utils/games";

interface GameInfoProps {
  gameState: Record<string, unknown> | null;
  playerColor: string;
}

function colorDot(color: string, sizeClass = "w-5 h-5") {
  if (color === "white") return `${sizeClass} bg-white border-2 border-gray-300 rounded-full`;
  if (color === "black") return `${sizeClass} bg-gray-800 border-2 border-gray-500 rounded-full`;
  const bg = LUDO_COLORS[color] ?? "bg-gray-500";
  return `${sizeClass} ${bg} border-2 border-gray-600 rounded-full`;
}

export default function GameInfo({ gameState, playerColor }: GameInfoProps) {
  const currentPlayer = (gameState?.current_player as string) ?? "white";
  const moveNumber = (gameState as Record<string, number>)?.fullmove_number;
  const winner = (gameState as Record<string, string | undefined>)?.vencedor;
  const isDraw = winner === "draw";
  const gameOver = !!winner;

  if (gameOver) {
    return (
      <div className="flex items-center justify-center w-full max-w-[640px] mb-4 px-2">
        <div className="flex items-center gap-3 text-xl font-bold">
          {isDraw ? (
            <span className="text-yellow-400">Empate!</span>
          ) : (
            <>
              <span className={colorDot(winner, "w-6 h-6")} />
              <span className="capitalize text-green-400">
                {PLAYER_NAMES[winner] ?? winner} venceu!
              </span>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between w-full max-w-[640px] mb-4 px-2">
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-400">Você:</span>
        <span className={colorDot(playerColor)} />
        <span className="capitalize font-medium">
          {PLAYER_NAMES[playerColor] ?? playerColor}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-400">Turno:</span>
        <span className={`${colorDot(currentPlayer)} animate-pulse`} />
        <span className="capitalize font-medium">
          {PLAYER_NAMES[currentPlayer] ?? currentPlayer}
        </span>
        {moveNumber !== undefined && (
          <span className="text-sm text-gray-400 ml-4">
            Movimento #{moveNumber}
          </span>
        )}
      </div>
    </div>
  );
}
