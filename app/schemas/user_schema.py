from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str