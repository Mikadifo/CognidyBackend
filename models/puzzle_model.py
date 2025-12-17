from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

class PuzzleMetadata(BaseModel):
    title: str = Field(..., example="Generated from sample.pdf")
    difficulty: str = Field(..., example="medium")
    gridSize: Dict[str, int] = Field(..., example={"rows": 15, "cols": 15})
    totalWords: int = Field(..., example=8)

class PuzzleWord(BaseModel):
    number: int = Field(..., example=1)
    word: str = Field(..., example="PYTHON")
    direction: str = Field(..., example="across")
    startRow: int = Field(..., example=0)
    startCol: int = Field(..., example=3)
    length: int = Field(..., example=6)
    hint: str = Field(..., example="Programming language")

class PuzzleHints(BaseModel):
    across: List[Dict[str, Any]] = Field(..., example=[{"number": 1, "hint": "Programming language"}])
    down: List[Dict[str, Any]] = Field(..., example=[{"number": 2, "hint": "Data structure"}])

class CrosswordPuzzleData(BaseModel):
    metadata: PuzzleMetadata
    grid: List[List[Optional[str]]] = Field(..., example=[[None, "P", "Y"], ["T", "H", "O"], [None, "N", None]])
    words: List[PuzzleWord]
    hints: PuzzleHints

class CrosswordPuzzle(BaseModel):
    user_id: str = Field(..., example="user123")
    puzzle_id: str = Field(..., example="1698765432123")
    puzzle_data: CrosswordPuzzleData
    created_at: datetime = Field(..., example="2023-01-01T00:00:00Z")
    completed: bool = Field(default=False, example=False)
    completion_time: Optional[datetime] = Field(default=None, example=None)