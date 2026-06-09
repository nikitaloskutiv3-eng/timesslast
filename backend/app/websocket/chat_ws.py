from fastapi import WebSocket, Depends, status
from sqlalchemy.orm import Session
import json

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services import message_service
from app.models.user import User

class ConnectionManager:
    def __init__(self):
        # chat_id -> список подключений
        self.active_connections: dict[int, list[dict]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append({
            "websocket": websocket,
            "user_id": user_id
        })

    def disconnect(self, chat_id: int, websocket: WebSocket):
        if chat_id in self.active_connections:
            self.active_connections[chat_id] = [
                conn for conn in self.active_connections[chat_id]
                if conn["websocket"] != websocket
            ]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, chat_id: int, message: dict):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                try:
                    await connection["websocket"].send_json(message)
                except:
                    pass

manager = ConnectionManager()