import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Session, StatusEnum
from app.schemas.schemas import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/sessions/{session_id}/chat")
async def chat(
    session_id: uuid.UUID,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status != StatusEnum.done:
        raise HTTPException(409, f"Session still {session.status.value}")

    service = ChatService()

    async def event_stream():
        async for chunk in service.stream_answer(
            session_id=str(session_id),
            question=body.message,
            history=body.history,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )