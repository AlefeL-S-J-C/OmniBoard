import { useState } from "react";

const GRID_SIZE = 7;

const POSITIONS: [number, number, number][] = [
  [0, 0, 0], [0, 3, 1], [0, 6, 2],
  [1, 1, 3], [1, 3, 4], [1, 5, 5],
  [2, 2, 6], [2, 3, 7], [2, 4, 8],
  [3, 0, 9], [3, 1, 10], [3, 2, 11], [3, 4, 12], [3, 5, 13], [3, 6, 14],
  [4, 2, 15], [4, 3, 16], [4, 4, 17],
  [5, 1, 18], [5, 3, 19], [5, 5, 20],
  [6, 0, 21], [6, 3, 22], [6, 6, 23],
];

const posGrid: (number | null)[][] = Array.from({ length: GRID_SIZE }, () =>
  Array.from({ length: GRID_SIZE }, () => null)
);
for (const [r, c, idx] of POSITIONS) {
  const row = posGrid[r];
  if (row) row[c] = idx;
}

const LINES: [[number, number], [number, number]][] = (() => {
  const lines: [[number, number], [number, number]][] = [];
  for (const [r, c, idx] of POSITIONS) {
    const adj = getAdjacent(idx);
    for (const adjIdx of adj) {
      const adjPos = POSITIONS.find(([, , i]) => i === adjIdx);
      if (adjPos) {
        const [ar, ac] = adjPos;
        if (r < ar || (r === ar && c < ac)) {
          lines.push([[r, c], [ar, ac]]);
        }
      }
    }
  }
  return lines;
})();

function getAdjacent(pos: number): number[] {
  const adj: Record<number, number[]> = {
    0: [1, 9], 1: [0, 2, 4], 2: [1, 14],
    3: [4, 10], 4: [1, 3, 5, 7], 5: [4, 13],
    6: [7, 11], 7: [4, 6, 8], 8: [7, 12],
    9: [0, 10, 21], 10: [3, 9, 11, 18], 11: [6, 10, 15],
    12: [8, 13, 17], 13: [5, 12, 14, 20], 14: [2, 13, 23],
    15: [11, 16], 16: [15, 17, 19], 17: [12, 16],
    18: [10, 19], 19: [16, 18, 20, 22], 20: [13, 19],
    21: [9, 22], 22: [19, 21, 23], 23: [14, 22],
  };
  return adj[pos] || [];
}

interface TrilhaBoardProps {
  gameState: {
    board: Record<number, string | null>;
    players: Record<string, { pieces_in_hand: number; pieces_on_board: number }>;
    current_player: string;
    phase: number;
    removing: boolean;
  };
  onMove: (move: Record<string, unknown>) => void;
  playerColor: string;
}

export default function TrilhaBoard({ gameState, onMove, playerColor }: TrilhaBoardProps) {
  const [selectedPos, setSelectedPos] = useState<number | null>(null);
  const [targetPositions, setTargetPositions] = useState<number[]>([]);

  const board = gameState.board;
  const currentPlayer = gameState.current_player;
  const phase = gameState.phase;
  const isMyTurn = currentPlayer === playerColor;

  // Phase names
  const phaseName = gameState.removing
    ? "Remover peça adversária"
    : phase === 1
    ? "Colocação"
    : phase === 2
    ? "Movimentação"
    : "Voo";

  const handlePosClick = (pos: number) => {
    if (!isMyTurn) return;

    if (gameState.removing) {
      if (board[pos] && board[pos] !== playerColor) {
        onMove({ remove: pos });
      }
      return;
    }

    // Placement phase
    if (phase === 1) {
      if (board[pos] === null) {
        onMove({ place: pos });
      }
      return;
    }

    // Movement phase
    if (selectedPos === null) {
      if (board[pos] === playerColor) {
        setSelectedPos(pos);
        if (phase === 2) {
          setTargetPositions(getAdjacent(pos).filter((p) => board[p] === null));
        } else {
          setTargetPositions(
            Array.from({ length: 24 }, (_, i) => i).filter(
              (p) => board[p] === null
            )
          );
        }
      }
    } else {
      if (pos === selectedPos) {
        setSelectedPos(null);
        setTargetPositions([]);
        return;
      }
      if (targetPositions.includes(pos)) {
        onMove({ from: selectedPos, to: pos });
        setSelectedPos(null);
        setTargetPositions([]);
      } else if (board[pos] === playerColor) {
        setSelectedPos(pos);
        if (phase === 2) {
          setTargetPositions(getAdjacent(pos).filter((p) => board[p] === null));
        } else {
          setTargetPositions(
            Array.from({ length: 24 }, (_, i) => i).filter(
              (p) => board[p] === null
            )
          );
        }
      }
    }
  };

  const cellSize = 640 / GRID_SIZE;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="text-sm text-gray-400 mb-2">
        Fase: <span className="text-amber-400 font-medium">{phaseName}</span>
        {playerColor && (
          <span className="ml-4">
            Sua cor:{" "}
            <span
              className={`inline-block w-3 h-3 rounded-full ${
                playerColor === "white" ? "bg-white" : "bg-gray-800 border border-gray-500"
              }`}
            />
          </span>
        )}
      </div>

      <svg
        width={640}
        height={640}
        className="bg-gray-800 rounded-lg border-2 border-gray-600"
      >
        {/* Lines */}
        {LINES.map(([from, to], i) => (
          <line
            key={i}
            x1={from[1] * cellSize + cellSize / 2}
            y1={from[0] * cellSize + cellSize / 2}
            x2={to[1] * cellSize + cellSize / 2}
            y2={to[0] * cellSize + cellSize / 2}
            stroke="#555"
            strokeWidth={2}
          />
        ))}

        {/* Positions */}
        {POSITIONS.map(([r, c, idx]) => {
          const cx = c * cellSize + cellSize / 2;
          const cy = r * cellSize + cellSize / 2;
          const piece = board[idx];
          const isSelected = selectedPos === idx;
          const isValidTarget = targetPositions.includes(idx);
          const isEmpty = piece === null;

          return (
            <g
              key={idx}
              onClick={() => handlePosClick(idx)}
              className="cursor-pointer"
            >
              {/* Target indicator */}
              {isValidTarget && (
                <circle
                  cx={cx}
                  cy={cy}
                  r={cellSize / 3}
                  fill="none"
                  stroke="rgba(34, 197, 94, 0.6)"
                  strokeWidth={3}
                  strokeDasharray="4 2"
                />
              )}

              {/* Position dot */}
              <circle
                cx={cx}
                cy={cy}
                r={isEmpty && !isValidTarget ? 6 : cellSize / 3.5}
                fill={isEmpty ? "#333" : piece === "white" ? "#fff" : "#111"}
                stroke={
                  isSelected ? "#fbbf24" : isValidTarget ? "#22c55e" : "#666"
                }
                strokeWidth={isSelected || isValidTarget ? 3 : 1}
              />
            </g>
          );
        })}
      </svg>
    </div>
  );
}
