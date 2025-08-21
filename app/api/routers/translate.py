# app/api/routers/translate.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.wallet import Wallet
from app.infrastructure.db.models.transaction import Transaction, TransactionType
from app.infrastructure.db.models.translation import Translation
from app.domain.schemas.classes import TranslationIn, TranslationOut, TranslationOutQueued
from app.domain.services.bus import publish_task

router = APIRouter(prefix="/translate", tags=["Translate"])


@router.post("/queue", response_model=TranslationOutQueued)
async def translate_queue(
    data: TranslationIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.input_text or len(data.input_text.strip()) == 0:
        raise HTTPException(422, "input_text is empty")

    task_id = publish_task({
        "user_id": str(current_user.id),
        "input_text": data.input_text,
        "source_lang": data.source_lang,
        "target_lang": data.target_lang,
        "model": getattr(data, "model", "marian"),
    })
    return {"task_id": task_id, "status": "queued"}

@router.get("/task/{task_id}", response_model=TranslationOutQueued)
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Translation).where(Translation.external_id == task_id))
    tr = result.scalar_one_or_none()
    if not tr:
        return {"task_id": task_id, "status": "pending"}
    return {"task_id": task_id, "status": "done", "output_text": tr.output_text, "cost": tr.cost}

# --- СИНХРОННЫЙ ПЕРЕВОД ПО /translate
@router.post("", response_model=TranslationOut)  # путь "/translate"
async def translate_sync(
    data: TranslationIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text = getattr(data, "input_text", None) or getattr(data, "text", None)
    source = getattr(data, "source_lang", None)
    target = getattr(data, "target_lang", None)

    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=422, detail="input_text is empty")

    # найдём/создадим кошелёк
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet: Wallet | None = result.scalar_one_or_none()
    if wallet is None:
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.add(wallet)
        await db.flush()

    # считаем стоимость
    cost = 1

    # имитация перевода
    output = text

    # записываем перевод
    tr = Translation(
        user_id=current_user.id,
        input_text=text,
        output_text=output,
        source_lang=data.source_lang,
        target_lang=data.target_lang,
        cost=cost if wallet.balance >= cost else 0,
    )
    db.add(tr)

    # списание только если хватает средств
    if wallet.balance >= cost:
        wallet.balance -= cost
        txn = Transaction(
            user_id=current_user.id,
            amount=1,
            type=TransactionType.DEBIT.value,  # << строка "DEBIT"
        )
        db.add(txn)

    await db.commit()
    # возвращаем из ORM в Pydantic v2
    return TranslationOut.model_validate(tr)
