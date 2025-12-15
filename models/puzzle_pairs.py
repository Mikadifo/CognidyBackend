from pydantic import BaseModel, Field

MAX_PUZZLES = 15

class PuzzlePair(BaseModel):
    left: str = Field(..., description="Left")
    right: str = Field(..., description="Right")
