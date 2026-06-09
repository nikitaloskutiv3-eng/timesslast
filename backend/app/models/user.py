from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    usernameid = Column(String, unique=True, index=True)
    accountid = Column(String, unique=True, nullable=False)
    bio = Column(String, default="")  # Пустая строка по умолчанию
    birthday = Column(String, default="")  # Пустая строка по умолчанию
    avatar = Column(String, nullable=True)
    status = Column(String, default="offline")  # 👈 Новое поле
    last_seen = Column(DateTime, default=datetime.utcnow) 

    # отношения
    messages = relationship("Message", back_populates="user")
    chats = relationship("Chat", secondary="chat_members", back_populates="members")