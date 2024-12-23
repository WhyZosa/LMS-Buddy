from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configs.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """
    Получение сессии для взаимодействия с базой данных.
    """
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None