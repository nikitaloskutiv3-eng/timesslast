from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 🔧 Строка подключения (SQLite для примера)
DATABASE_URL = "sqlite:///./test.db"

# 🚀 Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # только для SQLite
)

# 🏭 Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔌 Dependency для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()