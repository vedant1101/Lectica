import asyncio
import logging
from pathlib import Path
from typing import List

from app.models.models import Session, StatusEnum
from app.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

MODALITY_MAP = {
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg", ".flac"},
    "image": {".jpg", ".jpeg", ".png", ".webp", ".gif"},
    "text":  {".txt", ".md", ".pdf", ".docx"},
}


def detect_modality(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    for modality, extensions in MODALITY_MAP.items():
        if ext in extensions:
            return modality
    return "text"


class Orchestrator:

    async def process(self, session_id: str, files: List[dict]) -> None:
        async with AsyncSessionLocal() as db:
            session = await db.get(Session, session_id)
            session.status = StatusEnum.processing
            await db.commit()

        try:
            # Group by modality
            grouped = {"video": [], "audio": [], "image": [], "text": []}
            for f in files:
                modality = detect_modality(f["filename"])
                grouped[modality].append(f)

            # Import pipelines here to avoid circular imports
            from app.pipelines.text_pipeline import TextPipeline
            from app.pipelines.vision_pipeline import VisionPipeline
            from app.pipelines.audio_pipeline import AudioPipeline
            from app.pipelines.video_pipeline import VideoPipeline

            # Run all pipelines concurrently
            tasks = []
            if grouped["text"]:
                tasks.append(TextPipeline().run(session_id, grouped["text"]))
            if grouped["image"]:
                tasks.append(VisionPipeline().run(session_id, grouped["image"]))
            if grouped["audio"]:
                tasks.append(AudioPipeline().run(session_id, grouped["audio"]))
            if grouped["video"]:
                tasks.append(VideoPipeline().run(session_id, grouped["video"]))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, Exception):
                    logger.error(f"Pipeline error: {r}")

            # Generate study material from all chunks
            from app.services.study_service import StudyService
            await StudyService().generate_all(session_id)

            # Mark done
            async with AsyncSessionLocal() as db:
                session = await db.get(Session, session_id)
                session.status = StatusEnum.done
                await db.commit()

        except Exception as e:
            logger.exception(f"Orchestrator failed for session {session_id}: {e}")
            async with AsyncSessionLocal() as db:
                session = await db.get(Session, session_id)
                session.status = StatusEnum.failed
                await db.commit()