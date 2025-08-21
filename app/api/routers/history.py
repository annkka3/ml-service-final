#app/api/routers/history.py
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.infrastructure.db.database import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.transaction import Transaction
from app.infrastructure.db.models.translation import Translation
from app.domain.schemas.classes import TranslationItem, TransactionItem

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/translations", response_model=list[TranslationItem])
async def list_translations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    История переводов текущего пользователя.
    По умолчанию — последние 100 записей.
    """
    stmt = (
        select(Translation)
        .where(Translation.user_id == current_user.id)
        .order_by(desc(Translation.timestamp))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items


@router.get("/transactions", response_model=list[TransactionItem])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    История транзакций кошелька текущего пользователя.
    По умолчанию — последние 100 записей.
    """
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(desc(Transaction.timestamp))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return items


@router.get("/", response_model=list[TranslationItem], include_in_schema=False)
async def history_root(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_translations(skip=skip, limit=limit, db=db, current_user=current_user)

@router.get("", response_model=list[dict[str, Any]])
async def history(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # забираем последние записи отдельно
    tr_stmt = (
        select(Translation)
        .where(Translation.user_id == current_user.id)
        .order_by(desc(Translation.timestamp))
        .limit(limit)
    )
    tx_stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(desc(Transaction.timestamp))
        .limit(limit)
    )

    tr_res = await db.execute(tr_stmt)
    tx_res = await db.execute(tx_stmt)
    translations = tr_res.scalars().all()
    transactions = tx_res.scalars().all()

    # приводим к единому виду, где у переводов есть source_text
    items: list[dict[str, Any]] = []

    for t in translations:
        items.append({
            "kind": "translation",
            "timestamp": t.timestamp,
            "source_text": t.input_text,     # <-- ключ, который ждут тесты
            "output_text": t.output_text,
            "source_lang": t.source_lang,
            "target_lang": t.target_lang,
            "cost": t.cost,
        })

    for tx in transactions:
        items.append({
            "kind": "transaction",
            "timestamp": tx.timestamp,
            "type": tx.type,
            "amount": tx.amount,
        })

    # общая сортировка по времени по убыванию и обрезка до limit
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items[:limit]