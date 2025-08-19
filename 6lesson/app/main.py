# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routers import auth, translate, wallet, history
from app.infrastructure.db.init_db import init as init_db
from app.infrastructure.db.config import get_settings
from app.presentation.web.router import router as web_router
from app.presentation.web import web

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG and getattr(settings, "INIT_DB_ON_START", False):
        await init_db()
    yield



app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

# статика (папка web/static)
STATIC_DIR = Path(__file__).resolve().parent / "presentation" / "web" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=str(getattr(settings, "CORS_ALLOW_ORIGINS", "*")).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# роуты
app.include_router(auth.router)
app.include_router(translate.router)
app.include_router(wallet.router)
app.include_router(history.router)
app.include_router(web_router)


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}

