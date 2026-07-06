const BOARD_SIZE = 9;
const CELL = 52;
const PAD = 26;
const TOTAL = CELL * (BOARD_SIZE - 1) + PAD * 2;
const STONE_R = CELL * 0.42;
const STAR_POINTS = new Set(["3,3", "3,5", "5,3", "5,5", "4,4"]);

interface GoStone {
  r: number;
  c: number;
  color: "B" | "W";
}

interface GoBoardProps {
  gameState: {
    board: string[][];
    current_player: string;
    captures: Record<string, number>;
    consecutive_passes: number;
  };
  onMove: (move: Record<string, unknown>) => void;
  playerColor: string;
}

export default function GoBoard({ gameState, onMove, playerColor }: GoBoardProps) {
  const rawBoard = gameState.board ?? [];
  const currentPlayer = gameState.current_player ?? "black";
  const captures = gameState.captures ?? { black: 0, white: 0 };
  const isMyTurn = currentPlayer === playerColor;

  const stones: GoStone[] = [];
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = rawBoard[r]?.[c];
      if (cell && cell !== ".") {
        stones.push({ r, c, color: cell as "B" | "W" });
      }
    }
  }

  const handleClick = (r: number, c: number) => {
    if (!isMyTurn) return;
    if (rawBoard[r]?.[c] !== ".") return;
    onMove({ position: `${String.fromCharCode(97 + c)}${BOARD_SIZE - r}` });
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ background: "#111" }} />
          <span className="text-gray-300">Preto: {captures.black}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-white border border-gray-400" />
          <span className="text-gray-300">Branco: {captures.white}</span>
        </div>
        <span className="text-gray-400">
          Turno: {currentPlayer === "black" ? "Preto" : "Branco"}
        </span>
      </div>

      <div className="relative" style={{ width: TOTAL, height: TOTAL }}>
        <svg width={TOTAL} height={TOTAL} className="absolute inset-0 rounded-lg shadow-2xl">
          <rect x="0" y="0" width={TOTAL} height={TOTAL} fill="#DEB887" rx="6" />

          {Array.from({ length: BOARD_SIZE }, (_, i) => (
            <line key={`gv${i}`} x1={PAD + CELL * i} y1={PAD} x2={PAD + CELL * i} y2={PAD + CELL * (BOARD_SIZE - 1)} stroke="#8B7355" strokeWidth="1" />
          ))}
          {Array.from({ length: BOARD_SIZE }, (_, i) => (
            <line key={`gh${i}`} x1={PAD} y1={PAD + CELL * i} x2={PAD + CELL * (BOARD_SIZE - 1)} y2={PAD + CELL * i} stroke="#8B7355" strokeWidth="1" />
          ))}

          {Array.from({ length: BOARD_SIZE }, (_, ri) =>
            Array.from({ length: BOARD_SIZE }, (_, ci) =>
              STAR_POINTS.has(`${ri},${ci}`) ? (
                <circle key={`sp${ri}-${ci}`} cx={PAD + CELL * ci} cy={PAD + CELL * ri} r="3.5" fill="#8B7355" />
              ) : null
            )
          )}

          {stones.map((s) => (
            <circle
              key={`s${s.r}-${s.c}`}
              cx={PAD + CELL * s.c}
              cy={PAD + CELL * s.r}
              r={STONE_R}
              fill={s.color === "B" ? "#222" : "#fff"}
              stroke={s.color === "W" ? "#999" : "none"}
              strokeWidth={s.color === "W" ? 1 : 0}
            />
          ))}
        </svg>

        <div style={{ position: "absolute", left: PAD, top: PAD, display: "grid", gridTemplateColumns: `repeat(${BOARD_SIZE}, ${CELL}px)`, gap: 0 }}>
          {Array.from({ length: BOARD_SIZE * BOARD_SIZE }, (_, i) => {
            const r = Math.floor(i / BOARD_SIZE);
            const c = i % BOARD_SIZE;
            const disabled = !isMyTurn || rawBoard[r]?.[c] !== ".";
            return (
                <button
                  key={`b${r}-${c}`}
                  onClick={() => handleClick(r, c)}
                  disabled={disabled}
                  className={disabled ? "" : "hover:bg-black/10 transition-colors"}
                  style={{
                    background: "transparent",
                    border: "none",
                    padding: 0,
                    cursor: disabled ? "default" : "pointer",
                    width: "100%",
                    height: "100%",
                  }}
                />
              );
          })}
        </div>
      </div>

      {isMyTurn && (
        <button
          onClick={() => onMove({ position: "pass" })}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors"
        >
          Passar a vez
        </button>
      )}
    </div>
  );
}