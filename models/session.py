from datetime import date
from pydantic import BaseModel, Field, field_validator

class Session(BaseModel):
    section: str = Field(..., description="Cognidy Dashboard Section")
    completed_at: date = Field(..., description="Completion date")
    total: int = Field(..., ge=1)
    correct: int = Field(..., ge=0)

    @field_validator("section", mode="after")
    @classmethod
    def non_empty_strip(cls, value: str, info) -> str:
        value = value.strip()

        if not value:
            raise ValueError(f"{info.field_name} must not be empty")

        return value

    @field_validator("completed_at", mode="after")
    @classmethod
    def not_in_past(cls, value: date) -> date:
        today = date.today()

        if value < today:
            raise ValueError("completed_at cannot be in the past")

        return value
