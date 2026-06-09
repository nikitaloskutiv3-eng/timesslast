from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.chat import ChatResponse, PrivateChatCreate
from app.services import chat_service
from app.db.session import get_db
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.get("/", response_model=List[ChatResponse])
def get_my_chats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Получить все чаты текущего пользователя"""
    chats = chat_service.get_user_chats(db, current_user.id)
    
    # Добавляем имя собеседника
    result = []
    for chat in chats:
        chat_name = chat_service.get_chat_name(chat, current_user.id)
        result.append({
            "id": chat.id,
            "name": chat_name,
            "is_private": chat.is_private,
            "members": [member.id for member in chat.members]
        })
    
    return result

@router.post("/private", response_model=ChatResponse)
def create_or_get_private_chat(
    data: PrivateChatCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Создать или получить приватный чат с пользователем"""
    chat = chat_service.get_or_create_private_chat(
        db,
        current_user.id,
        data.user_id
    )
    
    chat_name = chat_service.get_chat_name(chat, current_user.id)
    
    return {
        "id": chat.id,
        "name": chat_name,
        "is_private": chat.is_private,
        "members": [member.id for member in chat.members]
    }