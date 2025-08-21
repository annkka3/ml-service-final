# app/infrastructure/db/models/wallet.py
from __future__ import annotations

import uuid
from sqlalchemy import Integer, String, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.infrastructure.db.database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_wallet_balance_nonneg"),
        Index("ix_wallet_user", "user_id"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="wallet")

    def __repr__(self) -> str:
        return f"<Wallet(user_id={self.user_id}, balance={self.balance})>"
