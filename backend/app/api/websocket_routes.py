from fastapi import APIRouter, WebSocket, Depends, Query
from sqlalchemy.orm import Session
import json

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services import message_service
from app.websocket.chat_ws import manager
from app.models.user import User
from app.schemas.message import MessageCreate

router = APIRouter()

@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(
    chat_id: int,
    websocket: WebSocket,
    token: str = Query(None),
    db: Session = Depends(get_db)
):
    """WebSocket для сообщений в чате"""
    
    if not token:
        await websocket.close(code=1008, reason="No token provided")
        return
    
    try:
        from app.services import auth_service
        from jose import jwt, JWTError
        
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        accountid: str = payload.get("sub")  # 👈 Теперь это accountid
        if accountid is None:
            await websocket.close(code=1008, reason="Invalid token")
            return
            
        # 👈 Ищем по accountid
        user = db.query(User).filter(User.accountid == accountid).first()
        if user is None:
            await websocket.close(code=1008, reason="User not found")
            return
            
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await manager.connect(chat_id, websocket, user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            message_data = MessageCreate(
                chat_id=chat_id,
                content=data
            )
            message = message_service.send_message(db, message_data, user.id)
            
            await manager.broadcast(chat_id, {
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "created_at": message.created_at.isoformat()
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(chat_id, websocket)