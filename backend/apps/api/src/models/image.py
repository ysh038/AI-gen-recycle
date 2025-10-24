from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from src.models.database import Base  # ✅ database.py에서 가져오기

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    object_key = Column(String(500), unique=True, nullable=False, index=True)
    filename = Column(String(500))
    content_type = Column(String(100))
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)