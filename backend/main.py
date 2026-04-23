import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SolveRequest, SolveResponse
from solver import solve_urjo

app = FastAPI(title="Urjo Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/solve", response_model=SolveResponse)
def solve_puzzle(request: SolveRequest):
    grid = request.grid
    clues = request.clues
    
    n = len(grid)
    if n == 0 or any(len(row) != n for row in grid):
        raise HTTPException(status_code=400, detail="Grid must be a non-empty square matrix.")
    if len(clues) != n or any(len(row) != n for row in clues):
        raise HTTPException(status_code=400, detail="Clues must match the grid dimensions.")
        
    start_time = time.time()
    solution = solve_urjo([row[:] for row in grid], clues)
    end_time = time.time()
    
    if solution:
        return SolveResponse(
            success=True, 
            solution=solution, 
            message=f"Solved in {(end_time - start_time):.4f} seconds"
        )
    else:
        return SolveResponse(
            success=False, 
            solution=None, 
            message="No solution exists for the given puzzle configuration."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
