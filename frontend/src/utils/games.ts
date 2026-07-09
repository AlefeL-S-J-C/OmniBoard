export interface GameInfo {
  id: string;
  name: string;
  boardSize: number;
}

export const GAMES: GameInfo[] = [
  { id: "chess", name: "Xadrez", boardSize: 8 },
  { id: "checkers", name: "Dama", boardSize: 8 },
  { id: "reversi", name: "Reversi", boardSize: 8 },
  { id: "go", name: "Go", boardSize: 9 },
  { id: "ludo", name: "Ludo", boardSize: 15 },
  { id: "trilha", name: "Trilha", boardSize: 7 },
];

export const PIECE_SYMBOLS: Record<string, Record<string, string>> = {
  chess: {
    K: "\u2654", Q: "\u2655", R: "\u2656", B: "\u2657", N: "\u2658", P: "\u2659",
    k: "\u265A", q: "\u265B", r: "\u265C", b: "\u265D", n: "\u265E", p: "\u265F",
  },
  checkers: {
    w: "\u2B24", W: "\u2B24", b: "\u25EF", B: "\u25EF",
  },
  reversi: {
    B: "\u25CF", W: "\u25CB",
  },
  go: {
    B: "\u25CF", W: "\u25CB",
  },
};

const PIECE_COLORS: Record<string, Record<string, string>> = {
  checkers: {
    w: "text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]", 
    W: "text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]",
    b: "text-gray-900 drop-shadow-[0_1px_2px_rgba(255,255,255,0.4)]", 
    B: "text-gray-900 drop-shadow-[0_1px_2px_rgba(255,255,255,0.4)]",
  },
  reversi: {
    B: "text-gray-900 drop-shadow-[0_1px_2px_rgba(255,255,255,0.4)]", 
    W: "text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]",
  },
  go: {
    B: "text-gray-900", 
    W: "text-white",
  },
};

export function getPieceSymbol(gameType: string, piece: string): string {
  return PIECE_SYMBOLS[gameType]?.[piece] ?? piece;
}

export const WHITE_PIECE_STYLE: Record<string, string> = {
  color: "#f5f5f0",
  textShadow: "1px 1px 2px #000, -1px -1px 2px #000, 1px -1px 2px #000, -1px 1px 2px #000",
};

export const BLACK_PIECE_STYLE: Record<string, string> = {
  color: "#1a1a1a",
  textShadow: "1px 1px 2px #fff, -1px -1px 2px #fff, 1px -1px 2px #fff, -1px 1px 2px #fff",
};

export function getPieceColor(gameType: string, piece: string): string {
  if (gameType === "chess") {
    return "";
  }
  return PIECE_COLORS[gameType]?.[piece] ?? "text-white";
}

const PIECE_PLAYER_COLORS: Record<string, Record<string, string>> = {
  checkers: { w: "white", W: "white", b: "black", B: "black" },
  reversi: { B: "black", W: "white" },
  go: { B: "black", W: "white" },
};

export function getPiecePlayerColor(gameType: string, piece: string): string {
  if (gameType === "chess") {
    return piece === piece.toUpperCase() ? "white" : "black";
  }
  return PIECE_PLAYER_COLORS[gameType]?.[piece] ?? "white";
}

export const LUDO_COLORS: Record<string, string> = {
  red: "bg-red-600",
  green: "bg-green-600",
  yellow: "bg-yellow-500",
  blue: "bg-blue-600",
};

export const LUDO_COLORS_LIGHT: Record<string, string> = {
  red: "bg-red-400",
  green: "bg-green-400",
  yellow: "bg-yellow-300",
  blue: "bg-blue-400",
};

export const LUDO_COLORS_BORDER: Record<string, string> = {
  red: "border-red-700",
  green: "border-green-700",
  yellow: "border-yellow-600",
  blue: "border-blue-700",
};

export const PLAYER_NAMES: Record<string, string> = {
  white: "Branco",
  black: "Preto",
  red: "Vermelho",
  green: "Verde",
  yellow: "Amarelo",
  blue: "Azul",
};
