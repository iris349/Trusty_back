from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import LookupResponse


router = APIRouter(
    prefix="/lookup",
    tags=["Lookup"]
)


@router.get("/", response_model=LookupResponse)
def lookup_reported_target(
    target: str = Query(..., description="조회할 이메일 또는 전화번호"),
    db: Session = Depends(get_db)
):
    reports = db.query(Report).filter(Report.target_value == target).all()

    return {
        "reported": len(reports) > 0,
        "count": len(reports),
        "target": target,
        "reports": reports
    }