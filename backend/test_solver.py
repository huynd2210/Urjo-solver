from solver import solve_urjo

def test_empty_grid_4x4():
    # An empty 4x4 should be solvable
    grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    clues = [
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    
    solution = solve_urjo(grid, clues)
    assert solution is not None
    
    # Check equal R/B in rows/cols
    for row in solution:
        assert sum(1 for x in row if x == 1) == 2
        assert sum(1 for x in row if x == 2) == 2
        
    for c in range(4):
        col = [solution[r][c] for r in range(4)]
        assert sum(1 for x in col if x == 1) == 2
        assert sum(1 for x in col if x == 2) == 2

def test_unsolvable_grid():
    # 4x4 with 3 reds in a row
    grid = [
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    clues = [[None]*4]*4
    solution = solve_urjo(grid, clues)
    assert solution is None

def test_clue_logic():
    grid = [
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    clues = [
        [1, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    solution = solve_urjo(grid, clues)
    assert solution is not None

def test_image_puzzle():
    grid = [
        [1, 0, 0, 1],
        [2, 0, 2, 0],
        [0, 2, 0, 0],
        [0, 0, 0, 0]
    ]
    clues = [
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    
    solution = solve_urjo(grid, clues)
    assert solution is not None
    
    for row in solution:
        assert sum(1 for x in row if x == 1) == 2
        assert sum(1 for x in row if x == 2) == 2
        
    for c in range(4):
        col = [solution[r][c] for r in range(4)]
        assert sum(1 for x in col if x == 1) == 2
        assert sum(1 for x in col if x == 2) == 2

def test_image_puzzle_2():
    grid = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 0]
    ]
    clues = [
        [None, None, 1, None],
        [3, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    
    solution = solve_urjo(grid, clues)
    assert solution is not None
    
    for row in solution:
        assert sum(1 for x in row if x == 1) == 2
        assert sum(1 for x in row if x == 2) == 2
        
    for c in range(4):
        col = [solution[r][c] for r in range(4)]
        assert sum(1 for x in col if x == 1) == 2
        assert sum(1 for x in col if x == 2) == 2
