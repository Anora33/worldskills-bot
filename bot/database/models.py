from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean
from sqlalchemy.sql import func
from bot.database.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    competition = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    points = Column(Integer, default=0)
    language = Column(String, default="uz")
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
