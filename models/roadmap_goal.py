from pydantic import BaseModel, Field

MAX_GOALS = 20

class RoadmapGoal(BaseModel):
    order: int = Field(..., ge=1, le=MAX_GOALS)
    title: str = Field(..., description="Short title, 3 words")
    brief: str = Field(..., description="Short description")
    completed: bool = False
