import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Session, Flashcard, StatusEnum
from app.schemas.schemas import (
    SessionOut, FlashcardOut, FlashcardReview, QuizOut, SummaryOut
)
from app.services.study_service import StudyService
from app.services.sm2_service import SM2Service

router = APIRouter()


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session


@router.get("/sessions/{session_id}/flashcards", response_model=List[FlashcardOut])
async def get_flashcards(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    _assert_done(await db.get(Session, session_id))
    result = await db.execute(
        select(Flashcard)
        .where(Flashcard.session_id == session_id)
        .order_by(Flashcard.due_date)
    )
    return result.scalars().all()


@router.post("/sessions/{session_id}/flashcards/{card_id}/review",
             response_model=FlashcardOut)
async def review_flashcard(
    session_id: uuid.UUID,
    card_id: uuid.UUID,
    body: FlashcardReview,
    db: AsyncSession = Depends(get_db),
):
    card = await db.get(Flashcard, card_id)
    if not card or str(card.session_id) != str(session_id):
        raise HTTPException(404, "Flashcard not found")
    updated = SM2Service().review(card, body.quality)
    db.add(updated)
    await db.commit()
    await db.refresh(updated)
    return updated


@router.get("/sessions/{session_id}/quiz", response_model=QuizOut)
async def get_quiz(
    session_id: uuid.UUID,
    n: int = 5,
    db: AsyncSession = Depends(get_db),
):
    _assert_done(await db.get(Session, session_id))
    questions = await StudyService().generate_quiz(str(session_id), n=n)
    return QuizOut(session_id=session_id, questions=questions)


@router.get("/sessions/{session_id}/summary", response_model=SummaryOut)
async def get_summary(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    _assert_done(await db.get(Session, session_id))
    data = await StudyService().generate_summary(str(session_id))
    return SummaryOut(session_id=session_id, **data)


def _assert_done(session):
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status != StatusEnum.done:
        raise HTTPException(
            409,
            f"Session is still {session.status.value}. Retry when status is 'done'."
        )