# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# гарантируем, что папка для SQLite существует на старте
os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///./data/app.db"

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
