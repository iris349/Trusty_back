from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.post import Post
from app.models.comment import Comment

from app.schemas.post_schema import PostCreate, PostResponse
from app.schemas.comment_schema import CommentCreate, CommentResponse


router = APIRouter(
    prefix="/community",
    tags=["Community"]
)


# 글 작성
@router.post("/post", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):

    new_post = Post(
        user_id=1,
        title=post.title,
        content=post.content
    )

    db.add(new_post)

    db.commit()

    db.refresh(new_post)

    return new_post


# 글 목록 조회
@router.get("/post", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):

    posts = db.query(Post).all()

    return posts


# 글 상세 조회
@router.get("/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):

    post = db.query(Post).filter(Post.id == post_id).first()

    return post


# 댓글 작성
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

from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    post_id: int
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# 글 삭제 기능
@router.delete("/post/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="게시글이 존재하지 않습니다."
        )

    db.delete(post)

    db.commit()

    return {
        "message": "게시글 삭제 완료"
    }