from pydantic import BaseModel, Field

MAX_GOALS = 20

class RoadmapGoal(BaseModel):
    order: int = Field(..., ge=1, le=MAX_GOALS)
    title: str = Field(..., min_length=3, max_length=38, description="Short title, 3 words")
    brief: str = Field(..., description="Short description")
    completed: bool = False
