from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    # 분석을 수행한 사용자
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 사용자가 입력한 내용
    input_text = Column(Text, nullable=False)

    # 분석 결과
    risk_level = Column(String)

    score = Column(Integer)

    scam_type = Column(String)

    reason = Column(Text)

    # 생성 시간
    created_at = Column(DateTime, default=datetime.utcnow)