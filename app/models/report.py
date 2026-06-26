from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(20), nullable=False)  # email 또는 phone
    target_value = Column(String(255), nullable=False, index=True)
    scam_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    evidence_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)