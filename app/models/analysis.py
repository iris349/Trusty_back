from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    input_text = Column(Text, nullable=False)

    # 종합 결과
    risk_level = Column(String)
    score = Column(Integer)
    scam_type = Column(String)
    reason = Column(Text)

    # 세부 점수
    url_risk_score = Column(Integer)
    language_pattern_score = Column(Integer)
    sender_reliability_score = Column(Integer)
    urgency_score = Column(Integer)

    # 권장 행동(JSON 문자열 저장)
    recommended_actions = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)