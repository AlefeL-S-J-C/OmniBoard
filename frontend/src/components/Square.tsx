import type { ReactNode } from "react";

interface SquareProps {
  isLight: boolean;
  isSelected: boolean;
  isValidMove: boolean;
  onClick: () => void;
  children?: ReactNode;
}

export default function Square({
  isLight,
  isSelected,
  isValidMove,
  onClick,
  children,
}: SquareProps) {
  const bgColor = isLight ? "bg-amber-100" : "bg-amber-800";
  const selectedClass = isSelected ? "ring-4 ring-yellow-400 ring-inset" : "";
  const validMoveClass = isValidMove
    ? !children
      ? "after:absolute after:inset-0 after:m-auto after:w-4 after:h-4 after:rounded-full after:bg-green-500 after:opacity-60"
      : "ring-2 ring-red-500 ring-inset"
    : "";

  return (
    <button
      onClick={onClick}
      className={`relative flex items-center justify-center aspect-square ${bgColor} ${selectedClass} ${validMoveClass} transition-colors`}
    >
      {children}
    </button>
  );
}
