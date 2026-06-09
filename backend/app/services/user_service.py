from sqlalchemy.orm import Session
from app.models.user import User


def search_users(db: Session, query: str):
    return db.query(User).filter(User.username.ilike(f"%{query}%")).all()