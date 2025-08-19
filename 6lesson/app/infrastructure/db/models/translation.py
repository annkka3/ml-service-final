from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid

from app.infrastructure.db.database import Base


class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)


    external_id: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )

    input_text: Mapped[str] = mapped_column(String, nullable=False)
    output_text: Mapped[str] = mapped_column(String, nullable=False)

    source_lang: Mapped[str] = mapped_column(String, nullable=False)
    target_lang: Mapped[str] = mapped_column(String, nullable=False)


    cost: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="translations")
