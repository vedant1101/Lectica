from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.config import settings
import app.models.models  # noqa: F401

from app.api.v1 import ingest, study, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Lectica",
    description="Turn any lecture into a study companion",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(study.router,  prefix="/api/v1", tags=["study"])
app.include_router(chat.router,   prefix="/api/v1", tags=["chat"])


@app.get("/health")
async def health():
    return {"status": "ok"}