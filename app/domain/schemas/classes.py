# app/domain/schemas/classes.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator, computed_field
from uuid import UUID

# --------- Входные/выходные для синхронного перевода ---------

class TranslationIn(BaseModel):
    text: str | None = None
    input_text: str | None = None
    source_lang: str | None = None
    target_lang: str
    model: str = "marian"

    @model_validator(mode="before")
    def accept_text_alias(cls, data):
        if isinstance(data, dict):
            if "input_text" not in data and "text" in data:
                data = {**data, "input_text": data["text"]}
        return data

    @model_validator(mode="after")
    def _normalize(self):
        # склеиваем text → input_text если нужно
        if not self.input_text:
            self.input_text = self.text
        if not self.input_text:
            raise ValueError("text is required")
        # дефолт для source_lang
        if not self.source_lang:
            self.source_lang = "auto"
        return self


class TranslationOut(BaseModel):
    id: str
    source_text: str = Field(alias="input_text")
    output_text: str
    source_lang: str
    target_lang: str
    cost: int | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --------- Кошелёк ---------

class TopUpIn(BaseModel):
    amount: int = Field(..., gt=0)


class BalanceOut(BaseModel):
    balance: int


# --------- Элементы истории ---------

class TranslationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    timestamp: datetime
    source_lang: str
    target_lang: str
    input_text: str
    output_text: str
    cost: Optional[int] = None

    @computed_field(alias="source_text", return_type=str)  # <-- алиас для тестов
    def source_text(self) -> str:
        return self.input_text

class TransactionItem(BaseModel):
    id: str
    timestamp: datetime
    amount: int
    type: str
    model_config = ConfigDict(from_attributes=True)


# --------- Очередь переводов ---------

class TranslationOutQueued(BaseModel):
    task_id: str
    status: str
    output_text: Optional[str] = None
    cost: Optional[float] = None
