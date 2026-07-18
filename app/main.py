from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 데이터베이스 및 모델, 라우터 import
from app.database import engine, Base
from app.models.user import User
from app.models.analysis import Analysis
from app.models.report import Report
from app.models.lookup import Lookup
from app.models.post import Post
from app.models.comment import Comment
from app.routers import (
    community, auth, users, report, lookup, analysis
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

# --- CORS 설정: 여기서 딱 한 번만 정의합니다 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# --- 라우터 등록 ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(community.router)
app.include_router(report.router)
app.include_router(lookup.router)
app.include_router(analysis.router)

@app.get("/")
def root():
    return {"message": "Trusty backend run"}