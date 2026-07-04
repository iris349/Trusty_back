from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String, nullable=False)

    content = Column(Text, nullable=False)
    
    attachment = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)