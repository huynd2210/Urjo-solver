import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Cell } from './Cell';

describe('Cell Component', () => {
  it('renders an empty cell', () => {
    const { container } = render(<Cell value={0} clue={null} onClick={() => {}} onContextMenu={() => {}} />);
    expect(container.firstChild).toHaveClass('empty');
  });

  it('renders a red cell', () => {
    const { container } = render(<Cell value={1} clue={null} onClick={() => {}} onContextMenu={() => {}} />);
    expect(container.firstChild).toHaveClass('red');
  });

  it('renders a blue cell with a clue', () => {
    const { container } = render(<Cell value={2} clue={3} onClick={() => {}} onContextMenu={() => {}} />);
    expect(container.firstChild).toHaveClass('blue');
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('fires onClick event', () => {
    const handleClick = vi.fn();
    const { container } = render(<Cell value={0} clue={null} onClick={handleClick} onContextMenu={() => {}} />);
    if (container.firstChild) {
      fireEvent.click(container.firstChild as Element);
    }
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('fires onContextMenu event', () => {
    const handleContextMenu = vi.fn();
    const { container } = render(<Cell value={0} clue={null} onClick={() => {}} onContextMenu={handleContextMenu} />);
    if (container.firstChild) {
      fireEvent.contextMenu(container.firstChild as Element);
    }
    expect(handleContextMenu).toHaveBeenCalledTimes(1);
  });
});
