from typing import List
from pydantic import BaseModel, Field, field_validator

MAX_QUIZZES = 15

class RoadmapGoal(BaseModel):
    question: str = Field(..., description="Question")
    options: List[str] = Field(..., description="List of options")
    correct: str = Field(..., description="Correct option string")

    @field_validator("question", "correct", mode="after")
    @classmethod
    def non_empty_strip(cls, value: str, info) -> str:
        value = value.strip()

        if not value:
            raise ValueError(f"{info.field_name} must not be empty")

        return value

