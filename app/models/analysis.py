from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    input_text = Column(Text, nullable=False)

    risk_level = Column(String)

    scam_type = Column(String)

    reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)