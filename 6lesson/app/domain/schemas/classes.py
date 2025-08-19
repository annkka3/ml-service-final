
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class TranslationIn(BaseModel):
    input_text: str
    source_lang: str
    target_lang: str

class TranslationOut(BaseModel):
    output_text: str
    cost: int
    timestamp: str  # process_translation_request возвращает isoformat строку

class TopUpIn(BaseModel):
    amount: int = Field(..., gt=0)

class BalanceOut(BaseModel):
    balance: int

class TranslationItem(BaseModel):
    id: str
    timestamp: datetime
    input_text: str
    output_text: str
    source_lang: str
    target_lang: str
    cost: int
    model_config = ConfigDict(from_attributes=True)  # <-- pydantic v2

class TransactionItem(BaseModel):
    id: str
    timestamp: datetime
    amount: int
    type: str
    model_config = ConfigDict(from_attributes=True)  # <-- pydantic v2

class TranslationIn(BaseModel):
    input_text: str
    source_lang: str
    target_lang: str
    model: str = "marian"

class TranslationOutQueued(BaseModel):
    task_id: str
    status: str
    output_text: Optional[str] = None
    cost: Optional[float] = None
