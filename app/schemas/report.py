from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ReportCreate(BaseModel):
    report_type: str
    target_value: str
    scam_type: str
    description: str
    evidence_url: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    report_type: str
    target_value: str
    scam_type: str
    description: str
    evidence_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LookupResponse(BaseModel):
    reported: bool
    count: int
    target: str
    reports: List[ReportResponse]