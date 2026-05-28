from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import hash_password
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin, Token
from app.core.security import hash_password, verify_password, create_access_token
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        nickname=user.nickname
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }