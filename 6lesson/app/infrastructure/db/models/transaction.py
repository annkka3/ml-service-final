# app/infrastructure/db/models/transaction.py
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String, DateTime, Integer, ForeignKey, func, CheckConstraint, Enum as SAEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.database import Base


class TransactionType(str, Enum):
    TOPUP = "Пополнение"
    DEBIT = "Списание"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        Index("ix_transactions_user_time", "user_id", "timestamp"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # серверное UTC-время; если нужен UTC строго — настройте БД/таймзону
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType), default=TransactionType.DEBIT, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    def __str__(self) -> str:
        return f"{self.timestamp}: {self.type.value} {self.amount} by {self.user_id}"
