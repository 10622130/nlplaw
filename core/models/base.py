from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import timezone, datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True)  # LINE 用戶 ID 或一般用戶唯一 ID
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UserInput(Base):
    __tablename__ = 'user_inputs'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    input_text = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)  # 儲存ai回覆
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))