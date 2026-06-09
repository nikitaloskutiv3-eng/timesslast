from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict

from app.schemas.message import MessageCreate, MessageResponse, UnreadCountResponse
from app.services import message_service
from app.db.session import get_db
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

@router.post("/", response_model=MessageResponse)
def send_message(message: MessageCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return message_service.send_message(db, message, current_user.id)

@router.get("/", response_model=List[MessageResponse])
def get_messages(chat_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return message_service.get_messages(db, chat_id)

# ✅ Отметить сообщение как прочитанное
@router.put("/{message_id}/read", response_model=MessageResponse)
def mark_message_as_read(message_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return message_service.mark_message_as_read(db, message_id)

# ✅ Отметить все сообщения в чате как прочитанные
@router.put("/chat/{chat_id}/read-all")
def mark_chat_as_read(chat_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return message_service.mark_chat_as_read(db, chat_id, current_user.id)

# ✅ Получить количество непрочитанных сообщений для всех чатов
@router.get("/unread/counts", response_model=Dict[int, int])
def get_unread_counts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return message_service.get_unread_counts(db, current_user.id)
