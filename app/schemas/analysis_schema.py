from pydantic import BaseModel
from datetime import datetime


class AnalysisCreate(BaseModel):
    input_text: str


class AnalysisResponse(BaseModel):
    id: int
    user_id: int | None
    input_text: str
    risk_level: str | None
    score: int | None
    scam_type: str | None
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True