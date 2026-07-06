import { useState } from "react";
import type { Position } from "../types/chess";
import LudoBoard from "./LudoBoard";
import GoBoard from "./GoBoard";
import Square from "./Square";
import TrilhaBoard from "./TrilhaBoard";
import { squareToNotation } from "../utils/board";
import { getPieceSymbol, getPieceColor, getPiecePlayerColor } from "../utils/games";
import { WHITE_PIECE_STYLE, BLACK_PIECE_STYLE } from "../utils/games";

interface BoardProps {
  gameState: Record<string, unknown>;
  onMove: (move: Record<string, unknown>) => void;
  onRollDice?: () => void;
  playerColor: string;
  gameType: string;
}

const PLACEMENT_GAMES = new Set(["reversi"]);

function GridBoard({
  rawBoard,
  boardSize,
  onMove,
  playerColor,
  gameType,
  currentPlayer,
}: {
  rawBoard: (string | null)[][];
  boardSize: number;
  onMove: (move: Record<string, unknown>) => void;
  playerColor: string;
  gameType: string;
  currentPlayer?: string;
}) {
  const [selected, setSelected] = useState<Position | null>(null);

  const isPlacement = PLACEMENT_GAMES.has(gameType);
  const isMyTurn = currentPlayer === playerColor;

  const handleClick = (row: number, col: number) => {
    const raw = rawBoard[row]?.[col];

    if (isPlacement) {
      if (isMyTurn) {
        const to = squareToNotation(row, col, boardSize);
        onMove({ position: to });
      }
      return;
    }

    if (selected) {
      const from = squareToNotation(selected.row, selected.col, boardSize);
      const to = squareToNotation(row, col, boardSize);
      onMove({ from, to });
      setSelected(null);
    } else if (raw && raw !== "." && isMyTurn) {
      const piecePlayerColor = getPiecePlayerColor(gameType, raw as string);
      if (piecePlayerColor === playerColor) {
        setSelected({ row, col });
      }
    }
  };

  const isValidTarget = (row: number, col: number): boolean => {
    if (!selected) return false;
    if (row === selected.row && col === selected.col) return false;
    return true;
  };

  const renderCellContent = (rowIdx: number, colIdx: number) => {
    const raw = rawBoard[rowIdx]?.[colIdx];
    if (!raw || raw === ".") return null;

    if (gameType === "chess") {
      const symbol = getPieceSymbol("chess", raw as string);
      const style = (raw as string) === (raw as string).toUpperCase()
        ? WHITE_PIECE_STYLE
        : BLACK_PIECE_STYLE;
      return (
        <span className="text-4xl select-none" style={style}>
          {symbol}
        </span>
      );
    }

    const symbol = getPieceSymbol(gameType, raw as string);
    const color = getPieceColor(gameType, raw as string);
    return (
      <span className={`text-3xl select-none ${color}`}>
        {symbol}
      </span>
    );
  };

  return (
    <div
      className="grid border-4 border-amber-900 rounded-lg overflow-hidden shadow-2xl w-full"
      style={{
        maxWidth: 640,
        gridTemplateColumns: `repeat(${boardSize}, 1fr)`,
      }}
    >
      {Array.from({ length: boardSize * boardSize }, (_, i) => {
        const rowIdx = Math.floor(i / boardSize);
        const colIdx = i % boardSize;
        const isLight = (rowIdx + colIdx) % 2 === 0;

        return (
          <Square
            key={`${rowIdx}-${colIdx}`}
            isLight={gameType === "chess" ? (playerColor === "white" ? isLight : (rowIdx + colIdx) % 2 !== 0) : isLight}
            isSelected={selected?.row === rowIdx && selected?.col === colIdx}
            isValidMove={isValidTarget(rowIdx, colIdx)}
            onClick={() => handleClick(rowIdx, colIdx)}
          >
            {renderCellContent(rowIdx, colIdx)}
          </Square>
        );
      })}
    </div>
  );
}

export default function Board({
  gameState,
  onMove,
  onRollDice,
  playerColor,
  gameType,
}: BoardProps) {
  const rawBoard = (gameState as { board?: unknown }).board;
  const boardArray = Array.isArray(rawBoard) ? rawBoard : [];
  const boardSize = boardArray.length || 8;
  const currentPlayer = (gameState as { current_player?: string })?.current_player;

  if (gameType === "ludo") {
    return (
      <LudoBoard
        gameState={gameState as Parameters<typeof LudoBoard>[0]["gameState"]}
        onMove={onMove}
        onRollDice={onRollDice}
        playerColor={playerColor}
      />
    );
  }

  if (gameType === "trilha") {
    return (
      <TrilhaBoard
        gameState={gameState as Parameters<typeof TrilhaBoard>[0]["gameState"]}
        onMove={onMove}
        playerColor={playerColor}
      />
    );
  }

  if (gameType === "go") {
    return (
      <GoBoard
        gameState={gameState as Parameters<typeof GoBoard>[0]["gameState"]}
        onMove={onMove}
        playerColor={playerColor}
      />
    );
  }

  return (
    <GridBoard
      rawBoard={boardArray}
      boardSize={boardSize}
      onMove={onMove}
      playerColor={playerColor}
      gameType={gameType}
      currentPlayer={currentPlayer}
    />
  );
}
