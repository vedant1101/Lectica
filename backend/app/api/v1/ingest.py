import os
import tempfile
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.models import Session
from app.schemas.schemas import IngestResponse

router = APIRouter()


@router.post("/sessions", response_model=IngestResponse)
async def create_session_and_ingest(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    # 1. Create session
    session = Session()
    db.add(session)
    await db.flush()
    session_id = str(session.id)

    # 2. Save uploaded files to temp dir
    saved_files = []
    tmp_dir = tempfile.mkdtemp(prefix=f"session_{session_id}_")

    for upload in files:
        dest = os.path.join(tmp_dir, upload.filename)
        content = await upload.read()
        with open(dest, "wb") as f:
            f.write(content)
        saved_files.append({
            "filename": upload.filename,
            "path": dest,
            "raw_text": None,
        })

    # 3. Dispatch orchestrator as background task
    from app.core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    background_tasks.add_task(
        orchestrator.process,
        session_id=session_id,
        files=saved_files,
    )

    return IngestResponse(
        session_id=session.id,
        status="processing",
        message=f"Processing {len(files)} file(s). Poll /api/v1/sessions/{session_id} for status.",
    )