from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse, UserSearchResponse, UserStatusUpdate
from app.db.session import get_db
from app.core.deps import get_current_user
from app.services import user_service
from app.models.user import User

# 📋 Схема для обновления профиля
class UserUpdate(BaseModel):
    username: Optional[str] = None
    usernameid: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[str] = None

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=List[UserSearchResponse])
def search_users(query: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return user_service.search_users(db, query)


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить профиль текущего пользователя"""
    
    if user_data.username:
        # Проверяем, что username не занят другим пользователем
        existing = db.query(User).filter(
            User.username == user_data.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_data.username
    
    if user_data.usernameid:
        # Проверяем, что usernameid не занят другим пользователем
        existing = db.query(User).filter(
            User.usernameid == user_data.usernameid,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="UserID already taken")
        current_user.usernameid = user_data.usernameid
    
    if user_data.bio is not None:
        current_user.bio = user_data.bio
    
    if user_data.birthday is not None:
        current_user.birthday = user_data.birthday
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



from datetime import datetime

@router.post("/me/status")
def update_user_status(
    status_data: UserStatusUpdate,  # 👈 используем схему
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.status = status_data.status
    current_user.last_seen = datetime.fromisoformat(status_data.last_seen.replace('Z', '+00:00'))
    db.commit()
    return {"status": "updated"}

@router.get("/{user_id}/status")
def get_user_status(user_id: int, db: Session = Depends(get_db)):
    """Получить статус пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"DEBUG: User {user.username} status: {user.status}, last_seen: {user.last_seen}")
    
    return {
        "status": user.status,
        "last_seen": user.last_seen.isoformat() if user.last_seen else None
    }