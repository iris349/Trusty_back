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
from app.core.security import get_current_user

from app.models.user import User
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
# 글 작성
# 로그인 필요
# ==========================
@router.post("/post", response_model=PostResponse)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attachment = None

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
        user_id=current_user.id,
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
# 로그인 불필요
# ==========================
@router.get("/post", response_model=list[PostResponse])
def get_posts(
    db: Session = Depends(get_db)
):
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .all()
    )

    return posts


# ==========================
# 글 상세 조회
# ==========================
@router.get("/post/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글이 존재하지 않습니다."
        )

    return post


# ==========================
# 댓글 작성
# 로그인 필요
# ==========================
@router.post("/comment", response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글이 존재하지 않습니다."
        )

    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content
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
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return comments


# ==========================
# 게시글 삭제
# 로그인 + 작성자 확인
# ==========================
@router.delete("/post/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="본인이 작성한 게시글만 삭제할 수 있습니다."
        )

    attachment_path = post.attachment

    db.delete(post)
    db.commit()

    if attachment_path and os.path.exists(attachment_path):
        os.remove(attachment_path)

    return {
        "message": "게시글 삭제 완료"
    }


# ==========================
# 댓글 삭제
# 로그인 + 작성자 확인
# ==========================
@router.delete("/comment/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="댓글을 찾을 수 없습니다."
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="본인이 작성한 댓글만 삭제할 수 있습니다."
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "댓글이 삭제되었습니다."
    }