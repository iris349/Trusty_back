from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    new_report = Report(
        report_type=report.report_type,
        target_value=report.target_value,
        scam_type=report.scam_type,
        description=report.description,
        evidence_url=report.evidence_url
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report