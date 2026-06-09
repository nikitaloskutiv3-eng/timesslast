from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services import auth_service
from app.core.deps import get_current_user

router = APIRouter()

class UserRegisterRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Register attempt for {user_data.username}")
    
    # Проверяем, что usernameid не занят (генерируем его из username и ID)
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = auth_service.register_user(db, user_data)
    # 👈 Генерируем usernameid как @user{id}
    new_user.usernameid = f"@{new_user.username}"
    new_user.accountid = f"acc_{new_user.id}"
    db.commit()
    db.refresh(new_user)
    
    # Используем usernameid для токена
    token = auth_service.create_access_token({"sub": new_user.accountid})
    
    return TokenResponse(
        access_token=token,
        user_id=new_user.id,
        username=new_user.username
    )

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLoginRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Login attempt for {user_data.username}")
    
    # Проверяем по usernameid вместо username
    user = db.query(User).filter(User.usernameid == user_data.username).first()
    
    if not user:
        print(f"DEBUG: User not found for {user_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not auth_service.verify_password(user_data.password, user.password_hash):
        print(f"DEBUG: Password verification failed for {user_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"DEBUG: Authentication successful for {user_data.username}")
    # Используем usernameid для токена
    token = auth_service.create_access_token({"sub": user.accountid})
    
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username
    )

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    print(f"DEBUG: /me endpoint called for user: {current_user.username}")
    
    return {
        "id": current_user.id,
        "accountid": current_user.accountid,
        "username": current_user.username,
        "usernameid": current_user.usernameid,
        "bio": current_user.bio,
        "birthday": current_user.birthday,
        "avatar": current_user.avatar
    }