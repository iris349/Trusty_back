from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    posts = relationship(
    "Post",
    back_populates="user",
    cascade="all, delete-orphan")

    comments = relationship(
    "Comment",
    back_populates="user",
    cascade="all, delete-orphan"
)
