from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.message import Message
from app.schemas.message import MessageCreate
from datetime import datetime
from typing import Dict

def send_message(db: Session, message_data: MessageCreate, sender_id: int) -> Message:
    new_message = Message(
        chat_id=message_data.chat_id,
        content=message_data.content,
        sender_id=sender_id,
        is_read=False  # ✅ По умолчанию не прочитано
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_messages(db: Session, chat_id: int):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()

# ✅ Отметить одно сообщение как прочитанное
def mark_message_as_read(db: Session, message_id: int) -> Message:
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.commit()
        db.refresh(message)
    return message

# ✅ Отметить все сообщения в чате как прочитанные
def mark_chat_as_read(db: Session, chat_id: int, user_id: int) -> Dict:
    """Отметить все сообщения в чате как прочитанные для текущего пользователя"""
    # Получаем все непрочитанные сообщения в чате, которые НЕ от текущего пользователя
    messages = db.query(Message).filter(
        and_(
            Message.chat_id == chat_id,
            Message.is_read == False,
            Message.sender_id != user_id  # Только чужие сообщения
        )
    ).all()
    
    for message in messages:
        message.is_read = True
        message.read_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "chat_id": chat_id,
        "marked_count": len(messages)
    }

# ✅ Получить количество непрочитанных сообщений для каждого чата
def get_unread_counts(db: Session, user_id: int) -> Dict[int, int]:
    """Получить словарь {chat_id: unread_count} для всех чатов пользователя"""
    # Считаем непрочитанные сообщения в каждом чате
    results = db.query(
        Message.chat_id,
        func.count(Message.id).label('unread_count')
    ).filter(
        and_(
            Message.is_read == False,
            Message.sender_id != user_id  # Только чужие сообщения
        )
    ).group_by(Message.chat_id).all()
    
    return {chat_id: count for chat_id, count in results}
