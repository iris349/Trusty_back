from pydantic import BaseModel
from datetime import datetime


# ==========================
# 분석 요청
# ==========================
class AnalysisCreate(BaseModel):
    input_text: str


# ==========================
# 분석 응답
# ==========================
class AnalysisResponse(BaseModel):
    id: int
    user_id: int

    input_text: str

    # 종합 결과
    risk_level: str
    score: int
    scam_type: str
    reason: str

    # 세부 점수
    url_risk_score: int
    language_pattern_score: int
    sender_reliability_score: int
    urgency_score: int

    # 권장 행동
    recommended_actions: list[str]

    created_at: datetime

    class Config:
        from_attributes = True