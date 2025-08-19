from __future__ import annotations

import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.infrastructure.db.database import Base
from app.core.utils.hasher import PasswordHasher
from app.core.utils.validator import UserValidator
from app.infrastructure.db.models.wallet import Wallet


class User(Base):
    __tablename__ = "users"

    # генерируем UUID4 строкой по умолчанию
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    _password_hash: Mapped[str] = mapped_column("password_hash", String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Связи
    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    translations: Mapped[list["Translation"]] = relationship(
        "Translation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @classmethod
    def create_instance(
        cls,
        email: str,
        password: str,
        is_admin: bool = False,
        initial_balance: int = 0,
        id: str | None = None,  # можно явно передать id при необходимости
    ) -> "User":
        UserValidator.validate_email(email)
        UserValidator.validate_password(password)

        return cls(
            id=id or str(uuid.uuid4()),
            email=email,
            _password_hash=PasswordHasher.hash(password),
            is_admin=is_admin,
            wallet=Wallet(balance=initial_balance),
        )

    def check_password(self, password: str) -> bool:
        return PasswordHasher.check(password, self._password_hash)

    @property
    def password_hash(self) -> str:
        return self._password_hash

