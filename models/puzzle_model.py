from pydantic import BaseModel, Field

class crosswordPuzzle(BaseModel):
    id: str = Field(..., example="puzzle123")
    title: str = Field(..., example="Sample Puzzle")
    grid: list[list[str]] = Field(..., example=[["", "A", ""], ["B", "", "C"], ["", "", "D"]])
    terms: list[str] = Field(..., example=["Word1", "Word2", "Word3"])
    definitions: list[str] = Field(..., example=["This is a sample word definition.", "Here is another sample", "last sample"])
    completed: bool = Field(..., example=False)

class PuzzleMetadata(BaseModel):
    description: str = Field(..., example="This is a sample puzzle description.")
    created_at: str = Field(..., example="2023-01-01T00:00:00Z")
