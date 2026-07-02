from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis_schema import AnalysisCreate, AnalysisResponse
from app.core.security import get_current_user

from app.services.llm_service import analyze_text

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


# ==========================
# 분석 요청
# ==========================
@router.post("", response_model=AnalysisResponse)
def create_analysis(
    request: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Gemini 분석
    result = analyze_text(request.input_text)

    new_analysis = Analysis(
        user_id=current_user.id,
        input_text=request.input_text,

        risk_level=result["risk_level"],
        score=result["score"],
        scam_type=result["scam_type"],
        reason=result["reason"]
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).all()

    return analyses


# ==========================
# 분석 횟수 조회
# 반드시 상세조회보다 위에!
# ==========================
@router.get("/count")
def get_analysis_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    count = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).count()

    return {
        "count": count
    }


# ==========================
# 분석 결과 상세 조회
# ==========================
@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="분석 결과가 없습니다."
        )

    return analysis