from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate

def send_message(db: Session, message_data: MessageCreate, sender_id: int) -> Message:
    new_message = Message(
        chat_id=message_data.chat_id,
        content=message_data.content,
        sender_id=sender_id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_messages(db: Session, chat_id: int):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()