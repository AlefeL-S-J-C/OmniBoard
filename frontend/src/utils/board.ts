import type { Board, PieceColor, PieceType, SquareContent } from "../types/chess";

const PIECE_MAP: Record<string, { type: PieceType; color: PieceColor }> = {
  K: { type: "king", color: "white" },
  Q: { type: "queen", color: "white" },
  R: { type: "rook", color: "white" },
  B: { type: "bishop", color: "white" },
  N: { type: "knight", color: "white" },
  P: { type: "pawn", color: "white" },
  k: { type: "king", color: "black" },
  q: { type: "queen", color: "black" },
  r: { type: "rook", color: "black" },
  b: { type: "bishop", color: "black" },
  n: { type: "knight", color: "black" },
  p: { type: "pawn", color: "black" },
};

export const PIECE_SYMBOLS: Record<PieceType, Record<PieceColor, string>> = {
  king: { white: "\u2654", black: "\u265A" },
  queen: { white: "\u2655", black: "\u265B" },
  rook: { white: "\u2656", black: "\u265C" },
  bishop: { white: "\u2657", black: "\u265D" },
  knight: { white: "\u2658", black: "\u265E" },
  pawn: { white: "\u2659", black: "\u265F" },
};

export function parseBoard(raw: string[][]): Board {
  return raw.map((row) =>
    row.map((cell): SquareContent => {
      if (cell === ".") return null;
      const mapped = PIECE_MAP[cell];
      if (!mapped) return null;
      return mapped;
    })
  );
}

export function squareToNotation(row: number, col: number, boardSize = 8): string {
  const file = String.fromCharCode(97 + col);
  const rank = boardSize - row;
  return `${file}${rank}`;
}

export function notationToSquare(notation: string, boardSize = 8): { row: number; col: number } | null {
  if (notation.length < 2) return null;
  const file = notation[0]!;
  const rankStr = notation.slice(1);
  const col = file.charCodeAt(0) - 97;
  const rank = parseInt(rankStr, 10);
  const row = boardSize - rank;
  if (col < 0 || col >= boardSize || row < 0 || row >= boardSize) return null;
  return { row, col };
}

export function getInitialBoard(): Board {
  const raw = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
  ];
  return parseBoard(raw);
}
