import React from 'react';
import { Cell } from './Cell';
import type { CellValue } from './Cell';

interface GridProps {
  size: number;
  grid: CellValue[][];
  clues: (number | null)[][];
  onCellClick: (row: number, col: number) => void;
  onCellContextMenu: (row: number, col: number, e: React.MouseEvent) => void;
}

export const Grid: React.FC<GridProps> = ({ size, grid, clues, onCellClick, onCellContextMenu }) => {
  return (
    <div 
      className="grid"
      style={{ 
        gridTemplateColumns: `repeat(${size}, 1fr)`,
        gridTemplateRows: `repeat(${size}, 1fr)`
      }}
    >
      {grid.map((row, r) => (
        row.map((cellValue, c) => (
          <Cell 
            key={`${r}-${c}`}
            value={cellValue}
            clue={clues[r]?.[c] ?? null}
            onClick={() => onCellClick(r, c)}
            onContextMenu={(e) => onCellContextMenu(r, c, e)}
          />
        ))
      ))}
    </div>
  );
};
