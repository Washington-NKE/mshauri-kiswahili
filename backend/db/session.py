import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings

logger = logging.getLogger("mshauri.db")

db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False

try:
    if "postgresql" in db_url:
        engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    else:
        engine = create_engine(db_url, connect_args=connect_args)
except Exception as e:
    logger.warning(f"Could not initialize primary database engine ({e}). Falling back to local SQLite.")
    db_url = "sqlite:///./mshauri.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def fallback_to_sqlite():
    global engine, SessionLocal
    logger.warning("Database connection error. Switching engine to local SQLite ('sqlite:///./mshauri.db').")
    engine = create_engine("sqlite:///./mshauri.db", connect_args={"check_same_thread": False})
    SessionLocal.configure(bind=engine)
    return engine


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
