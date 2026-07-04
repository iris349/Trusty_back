from pydantic import BaseModel
from datetime import datetime


# ==========================
# 게시글 작성
# ==========================
class PostCreate(BaseModel):
    title: str
    content: str


# ==========================
# 게시글 응답
# ==========================
class PostResponse(BaseModel):
    id: int
    user_id: int

    title: str
    content: str

    # ⭐ 첨부파일 경로
    attachment: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True