import { useState } from "react";
import { LUDO_COLORS, LUDO_COLORS_LIGHT, LUDO_COLORS_BORDER, PLAYER_NAMES } from "../utils/games";

const PLAYERS = ["red", "green", "yellow", "blue"] as const;

const BASE_OFFSETS: Record<string, [number, number] | undefined> = {
  green: [0, 0],
  yellow: [0, 9],
  blue: [9, 0],
  red: [9, 9],
};

const LUDO_PATH: [number, number, number][] = [
  [0, 6, 0], [0, 7, 1], [0, 8, 2], [1, 8, 3], [2, 8, 4], [3, 8, 5], [4, 8, 6], [5, 8, 7],
  [6, 8, 8], [6, 9, 9], [6, 10, 10], [6, 11, 11], [6, 12, 12], [6, 13, 13], [6, 14, 14],
  [7, 14, 15], [8, 14, 16], [8, 13, 17], [8, 12, 18], [8, 11, 19], [8, 10, 20], [8, 9, 21],
  [8, 8, 22], [9, 8, 23], [10, 8, 24], [11, 8, 25], [12, 8, 26], [13, 8, 27], [14, 8, 28],
  [14, 7, 29], [14, 6, 30], [13, 6, 31], [12, 6, 32], [11, 6, 33], [10, 6, 34], [9, 6, 35],
  [8, 6, 36], [8, 5, 37], [8, 4, 38], [8, 3, 39], [8, 2, 40], [8, 1, 41], [8, 0, 42],
  [7, 0, 43], [6, 0, 44], [6, 1, 45], [6, 2, 46], [6, 3, 47], [6, 4, 48], [6, 5, 49],
];

const HOME_STRETCH: Record<string, [number, number][] | undefined> = {
  red: [[13, 7], [12, 7], [11, 7], [10, 7], [9, 7], [8, 7]],
  green: [[1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6, 7]],
  yellow: [[7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6]],
  blue: [[7, 13], [7, 12], [7, 11], [7, 10], [7, 9], [7, 8]],
};

const ENTRY_POS: Record<string, number | undefined> = {
  red: 0, green: 13, yellow: 25, blue: 38,
};

const GATEWAY_TO_LUDO: Record<string, string> = {
  white: "red",
  black: "green",
};

interface PawnData {
  pos: number;
  home: boolean;
  stretch: number;
  done: boolean;
}

interface LudoBoardProps {
  gameState: {
    pawns: Record<string, PawnData[]>;
    current_player: string;
    dice: number | null;
  };
  onMove: (move: Record<string, unknown>) => void;
  onRollDice?: () => void;
  playerColor: string;
}

export default function LudoBoard({ gameState, onMove, onRollDice, playerColor }: LudoBoardProps) {
  const [selectedPawn, setSelectedPawn] = useState<number | null>(null);

  const pawns = gameState.pawns ?? {};
  const currentPlayer = gameState.current_player ?? "red";
  const dice = gameState.dice ?? null;
  const ludoColor = GATEWAY_TO_LUDO[playerColor] ?? playerColor;
  const isMyTurn = currentPlayer === ludoColor;

  const getPawnAtPathPos = (pathIdx: number): { player: string; pawnIdx: number } | null => {
    for (const player of PLAYERS) {
      const playerPawns = pawns[player] || [];
      for (let i = 0; i < playerPawns.length; i++) {
        const p = playerPawns[i];
        if (p && !p.home && !p.done && p.stretch < 0 && p.pos === pathIdx) {
          return { player, pawnIdx: i };
        }
      }
    }
    return null;
  };

  const getPawnInStretch = (player: string, stretchIdx: number): number | null => {
    const playerPawns = pawns[player] || [];
    for (let i = 0; i < playerPawns.length; i++) {
      const p = playerPawns[i];
      if (p && !p.done && p.stretch === stretchIdx) {
        return i;
      }
    }
    return null;
  };

  const handlePathClick = (pathIdx: number) => {
    if (!isMyTurn || dice === null) return;

    const pawn = getPawnAtPathPos(pathIdx);
    if (pawn && pawn.player === ludoColor) {
      setSelectedPawn(selectedPawn === pathIdx ? null : pathIdx);
      return;
    }

    if (selectedPawn !== null) {
      const playerPawns = pawns[ludoColor] || [];
      const pawnIdx = playerPawns.findIndex((p) => !p.home && !p.done && p.stretch < 0 && p.pos === selectedPawn);
      if (pawnIdx !== -1) {
        onMove({ pawn_index: pawnIdx });
        setSelectedPawn(null);
      }
    }
  };

  const handleHomePawnClick = (player: string, pawnIdx: number) => {
    if (!isMyTurn || dice !== 6) return;
    if (player === ludoColor) {
      onMove({ pawn_index: pawnIdx });
    }
  };

  const handleStretchClick = (pawnIdx: number) => {
    if (!isMyTurn || dice === null) return;
    onMove({ pawn_index: pawnIdx });
  };

  const handleRollDice = () => {
    if (!isMyTurn || dice !== null) return;
    if (onRollDice) onRollDice();
  };

  const renderPawn = (color: string, isSelected: boolean) => (
    <div
      className={`w-5 h-5 rounded-full border-2 ${LUDO_COLORS[color]} ${LUDO_COLORS_BORDER[color]} ${
        isSelected ? "ring-2 ring-white scale-125" : ""
      } shadow-md transition-all`}
    />
  );

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex items-center gap-4 text-sm">
        <span className="text-gray-400">Turno:</span>
        <span className={`flex items-center gap-2 px-3 py-1 rounded-full ${LUDO_COLORS[currentPlayer]} text-white font-medium`}>
          <span className={`w-3 h-3 rounded-full ${LUDO_COLORS[currentPlayer]} ring-1 ring-white`} />
          {PLAYER_NAMES[currentPlayer]}
        </span>
      </div>

      <div
        className="grid border-2 border-gray-600 rounded overflow-hidden shadow-2xl"
        style={{
          gridTemplateColumns: "repeat(15, 1fr)",
          width: 600,
          height: 600,
        }}
      >
        {Array.from({ length: 225 }, (_, i) => {
          const r = Math.floor(i / 15);
          const c = i % 15;

          for (const player of PLAYERS) {
            const offset = BASE_OFFSETS[player];
            if (!offset) continue;
            const [br, bc] = offset;
            if (r >= br && r < br + 6 && c >= bc && c < bc + 6) {
              const insideBorder = r >= br + 1 && r < br + 5 && c >= bc + 1 && c < bc + 5;
              if (insideBorder) {
                const idx = (r - br - 1) * 4 + (c - bc - 1);
                const pawnIdx = idx % 4;
                const playerPawns = pawns[player] || [];
                const pawn = playerPawns[pawnIdx];
                const hasPawn = pawn?.home && !pawn.done;
                return (
                  <div
                    key={i}
                    className={`flex items-center justify-center ${LUDO_COLORS_LIGHT[player]} border border-gray-700`}
                  >
                    {hasPawn && (
                      <button
                        onClick={() => handleHomePawnClick(player, pawnIdx)}
                        className="cursor-pointer"
                        title={`${PLAYER_NAMES[player]} peão ${pawnIdx + 1}`}
                      >
                        {renderPawn(player, false)}
                      </button>
                    )}
                  </div>
                );
              }
              return <div key={i} className={`${LUDO_COLORS[player]} border border-gray-700`} />;
            }
          }

          if (r >= 6 && r <= 8 && c >= 6 && c <= 8) {
            return (
              <div
                key={i}
                className="flex items-center justify-center bg-amber-50 border border-amber-300"
              >
                {r === 7 && c === 7 && (
                  <span className="text-lg font-bold text-amber-800" style={{ fontSize: 28 }}>&#9733;</span>
                )}
              </div>
            );
          }

          for (const [pl, stretch] of Object.entries(HOME_STRETCH)) {
            if (!stretch) continue;
            const stretchIdx = stretch.findIndex(([sr, sc]) => sr === r && sc === c);
            if (stretchIdx !== -1) {
              const pawnIdx = getPawnInStretch(pl, stretchIdx);
              return (
                <button
                  key={i}
                  onClick={() => pawnIdx !== null && handleStretchClick(pawnIdx)}
                  className={`flex items-center justify-center ${LUDO_COLORS[pl]} border border-gray-700 relative`}
                  disabled={pawnIdx === null}
                >
                  {pawnIdx !== null && renderPawn(pl, false)}
                </button>
              );
            }
          }

          const pathEntry = LUDO_PATH.find(([pr, pc]) => pr === r && pc === c);
          if (pathEntry) {
            const [, , pathIdx] = pathEntry;
            const pawn = getPawnAtPathPos(pathIdx);
            const isSelected = selectedPawn === pathIdx;
            const isEntry = Object.values(ENTRY_POS).includes(pathIdx);

            return (
              <button
                key={i}
                onClick={() => handlePathClick(pathIdx)}
                className={`flex items-center justify-center border border-gray-600 ${
                  isEntry ? "bg-amber-300" : "bg-amber-200"
                } hover:bg-amber-400 transition-colors relative`}
                title={pawn ? `${PLAYER_NAMES[pawn.player]} peão ${pawn.pawnIdx + 1}` : `Casa ${pathIdx + 1}`}
              >
                {isEntry && (
                  <span className="absolute text-[10px] text-amber-700 font-bold" style={{ top: 1, right: 2 }}>&#9733;</span>
                )}
                {pawn && renderPawn(pawn.player, isSelected)}
              </button>
            );
          }

          return <div key={i} className="bg-gray-900 border border-gray-800" />;
        })}
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={handleRollDice}
          disabled={!isMyTurn || dice !== null}
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 rounded-lg font-bold text-lg transition-colors"
        >
          {dice !== null ? (
            <span className="flex items-center gap-2">
              <span className="text-2xl">&#9856;{dice}</span>
            </span>
          ) : (
            "Rolar Dado"
          )}
        </button>
        <div className={`px-4 py-2 rounded-full text-sm font-medium ${LUDO_COLORS[currentPlayer]} text-white`}>
          {PLAYER_NAMES[currentPlayer]}
        </div>
      </div>

      {selectedPawn !== null && (
        <p className="text-sm text-amber-400 animate-pulse">
          Peão selecionado. Clique em uma casa vazia para mover.
        </p>
      )}
    </div>
  );
}
