from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)
from sqlalchemy.orm import Session

import os
import uuid

from app.database import get_db

from app.models.post import Post
from app.models.comment import Comment

from app.schemas.post_schema import PostResponse
from app.schemas.comment_schema import (
    CommentCreate,
    CommentResponse
)

router = APIRouter(
    prefix="/community",
    tags=["Community"]
)

# ==========================
# 업로드 폴더 생성
# ==========================
UPLOAD_DIR = "uploads/community"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==========================
# 글 작성 (파일 첨부 가능)
# ==========================
@router.post("/post", response_model=PostResponse)
async def create_post(

    title: str = Form(...),

    content: str = Form(...),

    file: UploadFile | None = File(None),

    db: Session = Depends(get_db)

):

    attachment = None

    # 파일이 있으면 저장
    if file:

        filename = f"{uuid.uuid4()}_{file.filename}"

        filepath = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())

        attachment = filepath

    new_post = Post(
        user_id=1,
        title=title,
        content=content,
        attachment=attachment
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# ==========================
# 글 목록 조회
# ==========================
@router.get("/post", response_model=list[PostResponse])
def get_posts(
    db: Session = Depends(get_db)
):

    posts = db.query(Post).all()

    return posts


# ==========================
# 글 상세 조회
# ==========================
@router.get("/post/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글이 존재하지 않습니다."
        )

    return post


# ==========================
# 댓글 작성
# ==========================
@router.post("/comment", response_model=CommentResponse)
def create_comment(

    comment: CommentCreate,

    db: Session = Depends(get_db)

):

    new_comment = Comment(
        post_id=comment.post_id,
        user_id=1,
        content=comment.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# ==========================
# 댓글 조회
# ==========================
@router.get(
    "/comment/{post_id}",
    response_model=list[CommentResponse]
)
def get_comments(

    post_id: int,

    db: Session = Depends(get_db)

):

    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).all()

    return comments


# ==========================
# 게시글 삭제
# ==========================
@router.delete("/post/{post_id}")
def delete_post(

    post_id: int,

    db: Session = Depends(get_db)

):

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글이 존재하지 않습니다."
        )

    # 첨부파일 삭제
    if post.attachment and os.path.exists(post.attachment):
        os.remove(post.attachment)

    db.delete(post)
    db.commit()

    return {
        "message": "게시글 삭제 완료"
    }