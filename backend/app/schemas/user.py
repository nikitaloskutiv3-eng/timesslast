from pydantic import BaseModel, Field
from typing import Optional


# 📥 Регистрация
class UserCreate(BaseModel):
    username: str
    password: str


# 🔐 Логин
class UserLogin(BaseModel):
    username: str
    password: str


# 📝 Обновление профиля
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    usernameid: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=150)  # 👈 Максимум 150 символов
    birthday: Optional[str] = None


# 📤 Ответ пользователю
class UserResponse(BaseModel):
    id: int
    username: str
    usernameid: str
    accountid: str
    bio: str
    birthday: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserSearchResponse(BaseModel):
    id: int
    username: str
    usernameid: str
    bio: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    status: str
    last_seen: str