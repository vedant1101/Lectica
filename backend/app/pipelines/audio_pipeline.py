import asyncio
import logging
from typing import List

from groq import AsyncGroq

from app.config import settings
from app.core.embedder import Embedder
from app.db.database import AsyncSessionLocal
from app.models.models import Chunk, ModalityEnum

logger = logging.getLogger(__name__)


class AudioPipeline:

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def run(self, session_id: str, files: List[dict]) -> None:
        embedder = Embedder()

        for file in files:
            path = file["path"]
            filename = file["filename"]

            try:
                # Transcribe using Groq Whisper API — no local install needed
                with open(path, "rb") as f:
                    transcription = await self.client.audio.transcriptions.create(
                        file=(filename, f.read()),
                        model="whisper-large-v3",
                        response_format="verbose_json",
                    )

                # Chunk transcript into segments
                segments = transcription.segments or []
                chunks_text = self._merge_segments(segments)

                if not chunks_text:
                    # Fallback — use full text as one chunk
                    chunks_text = [(transcription.text, 0.0)]

                async with AsyncSessionLocal() as db:
                    for i, (text, start_time) in enumerate(chunks_text):
                        embedding = await embedder.embed(text)
                        chunk = Chunk(
                            session_id=session_id,
                            modality=ModalityEnum.audio,
                            content=text,
                            source_ref=f"{filename} @ {self._fmt_time(start_time)}",
                            embedding=embedding,
                            metadata_={"chunk_index": i, "start_time": start_time},
                        )
                        db.add(chunk)
                    await db.commit()

                logger.info(f"Audio pipeline: {len(chunks_text)} chunks from {filename}")

            except Exception as e:
                logger.error(f"Audio pipeline failed for {filename}: {e}")
                raise

    def _merge_segments(self, segments: list, max_words: int = 150):
        chunks = []
        current_words = []
        current_start = 0.0

        for seg in segments:
            text = seg.get("text", "") if isinstance(seg, dict) else seg.text
            start = seg.get("start", 0.0) if isinstance(seg, dict) else seg.start
            words = text.strip().split()
            if not current_words:
                current_start = start
            current_words.extend(words)
            if len(current_words) >= max_words:
                chunks.append((" ".join(current_words), current_start))
                current_words = []

        if current_words:
            chunks.append((" ".join(current_words), current_start))

        return chunks

    def _fmt_time(self, seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"