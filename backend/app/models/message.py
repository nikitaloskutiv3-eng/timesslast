from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)  # ✅ Было: text
    sender_id = Column(Integer, ForeignKey("users.id"))  # ✅ Было: user_id
    chat_id = Column(Integer, ForeignKey("chats.id"))
    created_at = Column(DateTime, default=datetime.utcnow)  # ✅ Новое поле

    # связи
    user = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")