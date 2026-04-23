import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Grid } from './Grid';
import type { CellValue } from './Cell';

describe('Grid Component', () => {
  it('renders a grid of the correct size', () => {
    const size = 2;
    const grid: CellValue[][] = [[0, 1], [2, 0]];
    const clues: (number | null)[][] = [[null, 1], [null, null]];
    
    const { container } = render(
      <Grid size={size} grid={grid} clues={clues} onCellClick={() => {}} onCellContextMenu={() => {}} />
    );
    
    // 4 cells should be rendered
    const cells = container.querySelectorAll('.cell');
    expect(cells).toHaveLength(4);
    
    // Check specific cell states
    expect(cells[0]).toHaveClass('empty');
    expect(cells[1]).toHaveClass('red');
    expect(cells[2]).toHaveClass('blue');
    expect(cells[3]).toHaveClass('empty');
    
    // Check clue is rendered
    expect(screen.getByText('1')).toBeInTheDocument();
  });
});
