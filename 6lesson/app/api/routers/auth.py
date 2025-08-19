
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.infrastructure.db.config import get_settings
from app.core.security import create_access_token
from app.api.dependencies.auth import get_current_user
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.wallet import Wallet
from app.domain.schemas.auth import TokenOut, ProfileOut, RegisterIn, SignResponse, UserAuth

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=SignResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserAuth, db: AsyncSession = Depends(get_db)) -> SignResponse:
    """
    Регистрация пользователя. Создаёт пустой кошелёк.
    """
    email = data.email.lower()

    exists = await db.execute(select(User).where(User.email == email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = User(email=email)
    if hasattr(user, "set_password"):
        user.set_password(data.password)
    else:
        raise HTTPException(status_code=500, detail="User model missing set_password()")

    db.add(user)
    await db.flush()

    wallet = Wallet(user_id=user.id, balance=0)
    db.add(wallet)

    await db.commit()
    await db.refresh(user)

    return SignResponse(message="Registered", user_id=str(user.id))


@router.post("/login", response_model=TokenOut)
async def login(data: UserAuth, db: AsyncSession = Depends(get_db)) -> TokenOut:
    """
    Логин по email + password. Возвращает JWT access token.
    """
    email = data.email.lower()
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()

    if not user or not hasattr(user, "check_password") or not user.check_password(data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": str(user.id)},
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenOut(access_token=token)


@router.get("/me", response_model=ProfileOut)
async def me(current_user: User = Depends(get_current_user)) -> ProfileOut:
    return ProfileOut(id=str(current_user.id), email=current_user.email)

