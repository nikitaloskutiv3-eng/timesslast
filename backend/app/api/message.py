from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.message import MessageCreate, MessageResponse
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