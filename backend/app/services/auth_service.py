from datetime import datetime, timedelta
from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer

from app.models.user import User

# 🔐 настройки JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# ✅ OAuth2 для извлечения токена из заголовка
oauth2_scheme = HTTPBearer()

# Используем Argon2
ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def register_user(db: Session, user_data):
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise Exception("User already exists")

    new_user = User(
        username=user_data.username,
        usernameid=f"@{user_data.username}",  # 👈 usernameid = @username
        password_hash=hash_password(user_data.password),
        bio="",
        birthday="",
        avatar=None,
        accountid="temp" 
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Генерируем accountid
    new_user.accountid = f"acc_{new_user.id}"
    db.commit()
    db.refresh(new_user)

    return new_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"DEBUG: Created token: {encoded_jwt}")
    return encoded_jwt