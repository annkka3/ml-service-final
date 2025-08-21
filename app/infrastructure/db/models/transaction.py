# app/infrastructure/db/models/transaction.py
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.database import Base


class TransactionType(PyEnum):
    TOPUP = "TOPUP"
    DEBIT = "DEBIT"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    # ВАЖНО: храним строку, чтобы tests сравнивали tx.type со строками
    type: Mapped[str] = mapped_column(String(20), nullable=False)

    user = relationship("User", back_populates="transactions")

    def __str__(self) -> str:
        return f"{self.timestamp}: {self.type} {self.amount} by {self.user_id}"
