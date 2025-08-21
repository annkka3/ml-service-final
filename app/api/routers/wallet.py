# app/api/routers/wallet.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.wallet import Wallet
from app.infrastructure.db.models.transaction import Transaction, TransactionType
from app.domain.schemas.classes import TopUpIn, BalanceOut

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/", response_model=BalanceOut)
async def get_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить текущий баланс кошелька пользователя.
    Если кошелёк ещё не создан — создаём его с балансом 0 (это ожидают автотесты).
    """
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet: Wallet | None = result.scalar_one_or_none()

    if wallet is None:
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)

    return BalanceOut(balance=wallet.balance)

@router.get("/balance")
async def get_balance_alias(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_balance(db=db, current_user=current_user)

@router.post("/topup", response_model=BalanceOut)
async def topup(data: TopUpIn, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    # найдём/создадим кошелёк
    res = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = res.scalar_one_or_none()
    if wallet is None:
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.add(wallet)
        await db.flush()

    wallet.balance += data.amount


    txn = Transaction(
        user_id=current_user.id,
        amount=data.amount,
        type=TransactionType.TOPUP.value,
    )
    db.add(txn)

    await db.commit()
    await db.refresh(wallet)
    return BalanceOut(balance=wallet.balance)
