import React, { useState, useEffect } from 'react';
import { Grid } from './Grid';
import type { CellValue } from './Cell';

type StatusType = 'idle' | 'loading' | 'success' | 'error';

export const UrjoApp: React.FC = () => {
  const [size, setSize] = useState<number>(4);
  const [grid, setGrid] = useState<CellValue[][]>([]);
  const [clues, setClues] = useState<(number | null)[][]>([]);
  const [status, setStatus] = useState<StatusType>('idle');
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    handleReset(size);
  }, [size]);

  const handleReset = (newSize: number) => {
    setGrid(Array(newSize).fill(null).map(() => Array(newSize).fill(0)));
    setClues(Array(newSize).fill(null).map(() => Array(newSize).fill(null)));
    setStatus('idle');
    setMessage('');
  };

  const handleCellClick = (r: number, c: number) => {
    if (status === 'loading') return;
    const newGrid = [...grid];
    newGrid[r] = [...newGrid[r]];
    newGrid[r][c] = ((newGrid[r][c] + 1) % 3) as CellValue;
    setGrid(newGrid);
    setStatus('idle');
    setMessage('');
  };

  const handleCellContextMenu = (r: number, c: number, e: React.MouseEvent) => {
    e.preventDefault();
    if (status === 'loading') return;
    
    // Cycle clues: null -> 0 -> 1 ... -> 8 -> null
    const newClues = [...clues];
    newClues[r] = [...newClues[r]];
    const currentClue = newClues[r][c];
    if (currentClue === null) {
      newClues[r][c] = 0;
    } else if (currentClue >= 8) {
      newClues[r][c] = null;
    } else {
      newClues[r][c] = currentClue + 1;
    }
    setClues(newClues);
    setStatus('idle');
    setMessage('');
  };

  const handleSolve = async () => {
    setStatus('loading');
    setMessage('Solving...');
    
    try {
      const response = await fetch('http://localhost:8000/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid, clues }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setGrid(data.solution);
        setStatus('success');
        setMessage(data.message);
      } else {
        setStatus('error');
        setMessage(data.message || 'Failed to solve puzzle.');
      }
    } catch (error) {
      console.error(error);
      setStatus('error');
      setMessage('Failed to connect to solver API.');
    }
  };

  return (
    <div className="app-container anim-pop-in">
      <div className="header">
        <h1>Urjo Solver</h1>
        <p>Left-click to set colors (Red/Blue). Right-click to set numeric clues.</p>
      </div>

      <div className="controls">
        <select 
          value={size} 
          onChange={(e) => setSize(Number(e.target.value))}
          disabled={status === 'loading'}
        >
          <option value={4}>4x4 Grid</option>
          <option value={6}>6x6 Grid</option>
          <option value={8}>8x8 Grid</option>
          <option value={10}>10x10 Grid</option>
        </select>
        
        <button 
          className="btn-secondary" 
          onClick={() => handleReset(size)}
          disabled={status === 'loading'}
        >
          Reset
        </button>
        
        <button 
          className="btn-primary" 
          onClick={handleSolve}
          disabled={status === 'loading'}
        >
          Solve Puzzle
        </button>
      </div>

      <div className="game-board-container">
        {grid.length > 0 && (
          <Grid 
            size={size} 
            grid={grid} 
            clues={clues} 
            onCellClick={handleCellClick}
            onCellContextMenu={handleCellContextMenu}
          />
        )}
        
        {status !== 'idle' && (
          <div className={`status-message ${status}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};
