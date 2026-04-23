from pydantic import BaseModel
from typing import List, Optional

class SolveRequest(BaseModel):
    grid: List[List[int]]
    clues: List[List[Optional[int]]]

class SolveResponse(BaseModel):
    success: bool
    solution: Optional[List[List[int]]] = None
    message: Optional[str] = None
