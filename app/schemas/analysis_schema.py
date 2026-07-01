from pydantic import BaseModel
from datetime import datetime


# 분석 요청
class AnalysisCreate(BaseModel):
    input_text: str


# 분석 응답
class AnalysisResponse(BaseModel):
    id: int
    user_id: int

    input_text: str

    risk_level: str

    score: int

    scam_type: str

    reason: str

    created_at: datetime

    class Config:
        from_attributes = True