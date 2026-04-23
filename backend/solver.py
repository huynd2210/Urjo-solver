from typing import List, Tuple, Optional

def solve_urjo(grid: List[List[int]], clues: List[List[Optional[int]]]) -> Optional[List[List[int]]]:
    n = len(grid)
    if n == 0:
        return []
    
    # Pre-calculate neighbor coordinates for faster clue checking
    neighbors = {}
    for r in range(n):
        for c in range(n):
            adj = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n:
                        adj.append((nr, nc))
            neighbors[(r, c)] = adj

    def is_valid(g: List[List[int]], r: int, c: int) -> bool:
        # Check row counts
        row_red = sum(1 for val in g[r] if val == 1)
        row_blue = sum(1 for val in g[r] if val == 2)
        if row_red > n // 2 or row_blue > n // 2:
            return False
            
        # Check col counts
        col_red = sum(1 for g_row in g if g_row[c] == 1)
        col_blue = sum(1 for g_row in g if g_row[c] == 2)
        if col_red > n // 2 or col_blue > n // 2:
            return False

        # Check adjacent rows (only if fully filled)
        if r > 0 and 0 not in g[r] and 0 not in g[r-1]:
            if g[r] == g[r-1]:
                return False
        if r < n - 1 and 0 not in g[r] and 0 not in g[r+1]:
            if g[r] == g[r+1]:
                return False

        # Check adjacent cols (only if fully filled)
        col_c = [g_row[c] for g_row in g]
        if 0 not in col_c:
            if c > 0:
                col_prev = [g_row[c-1] for g_row in g]
                if 0 not in col_prev and col_c == col_prev:
                    return False
            if c < n - 1:
                col_next = [g_row[c+1] for g_row in g]
                if 0 not in col_next and col_c == col_next:
                    return False

        # Check clues
        for cr in range(n):
            for cc in range(n):
                clue = clues[cr][cc]
                if clue is not None:
                    color = g[cr][cc]
                    if color == 0:
                        continue
                    
                    same_count = 0
                    empty_count = 0
                    for nr, nc in neighbors[(cr, cc)]:
                        n_color = g[nr][nc]
                        if n_color == color:
                            same_count += 1
                        elif n_color == 0:
                            empty_count += 1
                            
                    if same_count > clue:
                        return False
                    if same_count + empty_count < clue:
                        return False

        return True

    def solve() -> bool:
        # Find minimum remaining values variable (MRV) or just first empty
        # For simplicity, first empty
        best_r, best_c = -1, -1
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 0:
                    best_r, best_c = r, c
                    break
            if best_r != -1:
                break
                
        if best_r == -1:
            return True # Solved!

        for color in [1, 2]:
            grid[best_r][best_c] = color
            if is_valid(grid, best_r, best_c):
                if solve():
                    return True
            grid[best_r][best_c] = 0
            
        return False

    # Check initial validity
    valid_initial = True
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                if not is_valid(grid, r, c):
                    valid_initial = False
                    break
    if not valid_initial:
        return None

    if solve():
        return grid
    return None
