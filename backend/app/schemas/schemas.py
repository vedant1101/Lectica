from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class SessionOut(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IngestResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    message: str


class FlashcardOut(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    source_ref: Optional[str]
    ease_factor: float
    interval: int
    due_date: datetime

    model_config = {"from_attributes": True}


class FlashcardReview(BaseModel):
    quality: int = Field(..., ge=0, le=5)


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str
    source_ref: Optional[str] = None


class QuizOut(BaseModel):
    session_id: uuid.UUID
    questions: List[QuizQuestion]


class SummaryOut(BaseModel):
    session_id: uuid.UUID
    title: str
    key_concepts: List[str]
    summary: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []