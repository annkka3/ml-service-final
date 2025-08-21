# app/infrastructure/db/models/translation.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, func, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.infrastructure.db.database import Base


class Translation(Base):
    __tablename__ = "translations"
    __table_args__ = (
        # cost может быть NULL (например, когда списание не произошло),
        # либо неотрицательное число
        CheckConstraint("cost IS NULL OR cost >= 0", name="ck_translations_cost_nonneg"),
        Index("ix_translations_user_time", "user_id", "timestamp"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # серверное время из БД — стабильнее, чем datetime.now() приложения
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    external_id: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )

    input_text: Mapped[str] = mapped_column(String, nullable=False)
    output_text: Mapped[str] = mapped_column(String, nullable=False)

    source_lang: Mapped[str] = mapped_column(String, nullable=False)
    target_lang: Mapped[str] = mapped_column(String, nullable=False)

    # допускаем NULL, если списание не произошло / бесплатный перевод
    cost: Mapped[int | None] = mapped_column(Integer, nullable=True, default=1)

    user: Mapped["User"] = relationship("User", back_populates="translations")
