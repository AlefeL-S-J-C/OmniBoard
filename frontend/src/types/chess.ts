export type PieceColor = "white" | "black";
export type PieceType = "king" | "queen" | "rook" | "bishop" | "knight" | "pawn";

export interface Piece {
  type: PieceType;
  color: PieceColor;
}

export type SquareContent = Piece | null;

export type Board = SquareContent[][];

export interface Position {
  row: number;
  col: number;
}

export interface Move {
  from: string;
  to: string;
}

export interface GameState {
  board: Board;
  current_player: PieceColor;
  castling_rights?: Record<string, boolean>;
  en_passant?: string | null;
  halfmove_clock?: number;
  fullmove_number?: number;
  [key: string]: unknown;
}

export interface WsMessage {
  action: string;
  payload?: Record<string, unknown>;
}

export interface WsEvent {
  evento: string;
  novo_estado?: GameState;
  message?: string;
}
