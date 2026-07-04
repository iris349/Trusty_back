import json

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

    result = analyze_text(request.input_text)

    new_analysis = Analysis(
        user_id=current_user.id,
        input_text=request.input_text,

        risk_level=result["risk_level"],
        score=result["score"],
        scam_type=result["scam_type"],
        reason=result["reason"],

        url_risk_score=result["url_risk_score"],
        language_pattern_score=result["language_pattern_score"],
        sender_reliability_score=result["sender_reliability_score"],
        urgency_score=result["urgency_score"],

        # 리스트 → 문자열로 저장
        recommended_actions=json.dumps(
            result["recommended_actions"],
            ensure_ascii=False
        )
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    # 문자열 → 리스트로 변환해서 응답
    return AnalysisResponse(
        id=new_analysis.id,
        user_id=new_analysis.user_id,
        input_text=new_analysis.input_text,

        risk_level=new_analysis.risk_level,
        score=new_analysis.score,
        scam_type=new_analysis.scam_type,
        reason=new_analysis.reason,

        url_risk_score=new_analysis.url_risk_score,
        language_pattern_score=new_analysis.language_pattern_score,
        sender_reliability_score=new_analysis.sender_reliability_score,
        urgency_score=new_analysis.urgency_score,

        recommended_actions=json.loads(
            new_analysis.recommended_actions
        ),

        created_at=new_analysis.created_at
    )


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

    result = []

    for analysis in analyses:
        result.append(
            AnalysisResponse(
                id=analysis.id,
                user_id=analysis.user_id,
                input_text=analysis.input_text,

                risk_level=analysis.risk_level,
                score=analysis.score,
                scam_type=analysis.scam_type,
                reason=analysis.reason,

                url_risk_score=analysis.url_risk_score,
                language_pattern_score=analysis.language_pattern_score,
                sender_reliability_score=analysis.sender_reliability_score,
                urgency_score=analysis.urgency_score,

                recommended_actions=json.loads(
                    analysis.recommended_actions
                ),

                created_at=analysis.created_at
            )
        )

    return result


# ==========================
# 분석 횟수 조회
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

    return AnalysisResponse(
        id=analysis.id,
        user_id=analysis.user_id,
        input_text=analysis.input_text,

        risk_level=analysis.risk_level,
        score=analysis.score,
        scam_type=analysis.scam_type,
        reason=analysis.reason,

        url_risk_score=analysis.url_risk_score,
        language_pattern_score=analysis.language_pattern_score,
        sender_reliability_score=analysis.sender_reliability_score,
        urgency_score=analysis.urgency_score,

        recommended_actions=json.loads(
            analysis.recommended_actions
        ),

        created_at=analysis.created_at
    )
