
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.database import get_db
from app.api.dependencies.auth import get_current_user
from app.infrastructure.db.models.user import User
from app.domain.schemas.classes import TranslationIn, TranslationOutQueued
from app.domain.services.bus import publish_task
from sqlalchemy import select
from app.infrastructure.db.models.translation import Translation

router = APIRouter(prefix="/translate", tags=["Translate"])

@router.post("/", response_model=TranslationOutQueued)
async def translate_queue(
    data: TranslationIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # простая валидация ещё до очереди
    if not data.input_text or len(data.input_text.strip()) == 0:
        raise HTTPException(422, "input_text is empty")

    task_id = publish_task({
        "user_id": str(current_user.id),
        "input_text": data.input_text,
        "source_lang": data.source_lang,
        "target_lang": data.target_lang,
        "model": data.model,
    })
    return {"task_id": task_id, "status": "queued"}

@router.get("/task/{task_id}", response_model=TranslationOutQueued)
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    # считаем, что воркер записывает Translation с external_id=task_id
    result = await db.execute(
        select(Translation).where(Translation.external_id == task_id)
    )
    tr = result.scalar_one_or_none()
    if not tr:
        return {"task_id": task_id, "status": "pending"}
    return {"task_id": task_id, "status": "done", "output_text": tr.output_text, "cost": tr.cost}
