from pydantic import BaseModel, Field, field_validator

MAX_GOALS = 20

class RoadmapGoal(BaseModel):
    order: int = Field(..., ge=1, le=MAX_GOALS)
    title: str = Field(..., description="Short title")
    brief: str = Field(..., description="Short description")
    completed: bool = False

    @field_validator("title", "brief", mode="after")
    @classmethod
    def non_empty_strip(cls, value: str, info) -> str:
        value = value.strip()

        if not value:
            raise ValueError(f"{info.field_name} must not be empty")

        return value
