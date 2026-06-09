from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Index
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
    is_read = Column(Boolean, default=False)  # ✅ Статус прочтения
    read_at = Column(DateTime, nullable=True)  # ✅ Время прочтения

    # связи
    user = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")
    
    # 🔹 Индекс для быстрого поиска непрочитанных сообщений
    __table_args__ = (
        Index('idx_chat_unread', 'chat_id', 'is_read'),
    )
