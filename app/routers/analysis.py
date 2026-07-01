from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.schemas.analysis_schema import (
    AnalysisCreate,
    AnalysisResponse
)

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


# ==========================
# 분석 요청
# ==========================
@router.post("", response_model=AnalysisResponse)
def create_analysis(
    analysis: AnalysisCreate,
    db: Session = Depends(get_db)
):

    new_analysis = Analysis(
        user_id=1,      # 추후 JWT 연동
        input_text=analysis.input_text,

        # 임시 더미 데이터
        risk_level="HIGH",
        score=95,
        scam_type="기관사칭",
        reason="임시 분석 결과입니다."
    )

    db.add(new_analysis)

    db.commit()

    db.refresh(new_analysis)

    return new_analysis


# ==========================
# 분석 기록 목록 조회
# ==========================
@router.get("", response_model=list[AnalysisResponse])
def get_analyses(
    db: Session = Depends(get_db)
):

    analyses = db.query(Analysis).all()

    return analyses


# ==========================
# 분석 횟수 조회
# 반드시 상세조회보다 위에!
# ==========================
@router.get("/count")
def get_analysis_count(
    db: Session = Depends(get_db)
):

    count = db.query(Analysis).count()

    return {
        "count": count
    }


# ==========================
# 분석 결과 상세 조회
# ==========================
@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="분석 결과가 없습니다."
        )

    return analysis