from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    chat_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool = False  # ✅ Статус прочтения
    read_at: Optional[datetime] = None  # ✅ Время прочтения

    class Config:
        from_attributes = True

class MarkMessageAsReadRequest(BaseModel):
    """Запрос на отметить сообщение как прочитанное"""
    pass

class UnreadCountResponse(BaseModel):
    """Ответ с количеством непрочитанных сообщений"""
    chat_id: int
    unread_count: int
