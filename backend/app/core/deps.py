from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services import auth_service

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services import auth_service

def get_current_user(
    token: str = Depends(auth_service.oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из JWT токена"""
    
    print(f"DEBUG: get_current_user called with token: {token}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_str = token.credentials if hasattr(token, 'credentials') else token
        
        print(f"DEBUG: token_str type: {type(token_str)}, value: {token_str}")
        
        payload = jwt.decode(
            token_str,
            auth_service.SECRET_KEY, 
            algorithms=[auth_service.ALGORITHM]
        )
        accountid: str = payload.get("sub")  # 👈 Теперь это accountid
        print(f"DEBUG: Decoded accountid: {accountid}")
        
        if accountid is None:
            print("DEBUG: Accountid is None")
            raise credentials_exception
            
    except JWTError as e:
        print(f"DEBUG: JWTError: {e}")
        raise credentials_exception
    
    # 👈 Ищем по accountid
    user = db.query(User).filter(User.accountid == accountid).first()
    print(f"DEBUG: Found user: {user}")
    
    if user is None:
        print("DEBUG: User not found in database")
        raise credentials_exception
    
    return user


