from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="인증 정보가 올바르지 않습니다.")

    except JWTError:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

    return user