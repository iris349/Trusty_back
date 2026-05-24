from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("posts.id"))

    user_id = Column(Integer, ForeignKey("users.id"))

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)