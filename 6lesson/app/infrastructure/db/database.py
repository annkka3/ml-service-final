# app/infrastructure/db/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.db.config import get_settings  # используем новый config.py

settings = get_settings()

# --- SQLAlchemy Base ---
class Base(DeclarativeBase):
    """Общий declarative Base для всех моделей."""
    pass

# --- DATABASE URL ---
DATABASE_URL = settings.DATABASE_URL_asyncpg

# --- Engine & sessions ---
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
SessionLocal = async_session  # alias для обратной совместимости

# --- Dependency ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
