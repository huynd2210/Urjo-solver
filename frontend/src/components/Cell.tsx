import React from 'react';

export type CellValue = 0 | 1 | 2; // 0: Empty, 1: Red, 2: Blue

interface CellProps {
  value: CellValue;
  clue: number | null;
  onClick: () => void;
  onContextMenu: (e: React.MouseEvent) => void;
}

export const Cell: React.FC<CellProps> = ({ value, clue, onClick, onContextMenu }) => {
  let colorClass = 'empty';
  if (value === 1) colorClass = 'red';
  else if (value === 2) colorClass = 'blue';

  return (
    <div 
      className={`cell ${colorClass}`} 
      onClick={onClick}
      onContextMenu={onContextMenu}
    >
      {clue !== null && (
        <div className="clue-number">
          {clue}
        </div>
      )}
    </div>
  );
};
