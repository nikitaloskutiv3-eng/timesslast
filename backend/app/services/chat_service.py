from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.user import User
from app.schemas.chat import ChatCreate

def get_or_create_private_chat(db: Session, user1_id: int, user2_id: int):
    """Получить или создать приватный чат между двумя пользователями"""
    
    # Ищем существующий чат
    chat = db.query(Chat).filter(
        Chat.is_private == True
    ).filter(
        Chat.members.any(User.id == user1_id)
    ).filter(
        Chat.members.any(User.id == user2_id)
    ).first()
    
    if chat:
        return chat
    
    # Если не найден, создаём новый
    user1 = db.query(User).get(user1_id)
    user2 = db.query(User).get(user2_id)
    
    new_chat = Chat(is_private=True)
    new_chat.members.append(user1)
    new_chat.members.append(user2)
    
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    return new_chat

def get_user_chats(db: Session, user_id: int):
    """Получить все чаты пользователя"""
    user = db.query(User).get(user_id)
    return user.chats

def get_chat_name(chat: Chat, current_user_id: int) -> str:
    """Получить имя чата - username собеседника или название группы"""
    if chat.is_private:
        # Найти второго пользователя в чате
        for member in chat.members:
            if member.id != current_user_id:
                return member.username
        return "Chat"
    else:
        return chat.name or "Group Chat"