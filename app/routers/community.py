from fastapi import APIRouter, Depends
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