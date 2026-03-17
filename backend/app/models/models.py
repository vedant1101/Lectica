import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Float, DateTime,
    ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import enum

from app.db.database import Base
from app.config import settings


class ModalityEnum(str, enum.Enum):
    text  = "text"
    image = "image"
    audio = "audio"
    video = "video"


class StatusEnum(str, enum.Enum):
    pending    = "pending"
    processing = "processing"
    done       = "done"
    failed     = "failed"


class Session(Base):
    __tablename__ = "sessions"

    id:         Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:      Mapped[str]       = mapped_column(String(255), nullable=True)
    status:     Mapped[StatusEnum]= mapped_column(SAEnum(StatusEnum), default=StatusEnum.pending)
    created_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks:     Mapped[list["Chunk"]]     = relationship("Chunk",     back_populates="session", cascade="all, delete")
    flashcards: Mapped[list["Flashcard"]] = relationship("Flashcard", back_populates="session", cascade="all, delete")


class Chunk(Base):
    __tablename__ = "chunks"

    id:         Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID]   = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"))
    modality:   Mapped[ModalityEnum]= mapped_column(SAEnum(ModalityEnum))
    content:    Mapped[str]         = mapped_column(Text)
    source_ref: Mapped[str]         = mapped_column(String(512), nullable=True)
    embedding:  Mapped[list[float]] = mapped_column(Vector(settings.EMBEDDING_DIM), nullable=True)
    metadata_:  Mapped[dict]        = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime]    = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship("Session", back_populates="chunks")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id:    Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"))
    question:      Mapped[str]       = mapped_column(Text)
    answer:        Mapped[str]       = mapped_column(Text)
    source_ref:    Mapped[str]       = mapped_column(String(512), nullable=True)
    ease_factor:   Mapped[float]     = mapped_column(Float, default=2.5)
    interval:      Mapped[int]       = mapped_column(Integer, default=1)
    repetitions:   Mapped[int]       = mapped_column(Integer, default=0)
    due_date:      Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)
    last_reviewed: Mapped[datetime]  = mapped_column(DateTime, nullable=True)
    created_at:    Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship("Session", back_populates="flashcards")