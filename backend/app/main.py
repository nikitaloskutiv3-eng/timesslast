from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base_class import Base
from app.db.session import engine

from app.models.user import User
from app.models.message import Message
from app.models.chat import Chat

from app.api import auth, chat, message, user
from app.api import websocket_routes

# 🔹 создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Messenger API")

# 🔹 CORS для локального фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Роуты
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router)
app.include_router(message.router)
app.include_router(user.router)
app.include_router(websocket_routes.router)