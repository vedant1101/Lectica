import asyncio
import logging
from typing import List

from app.core.embedder import Embedder
from app.db.database import AsyncSessionLocal
from app.models.models import Chunk, ModalityEnum

logger = logging.getLogger(__name__)

_whisper_model = None


def get_whisper_model(size: str = "base"):
    global _whisper_model
    if _whisper_model is None:
        import whisper
        logger.info(f"Loading Whisper model: {size}")
        _whisper_model = whisper.load_model(size)
    return _whisper_model


class AudioPipeline:

    async def run(self, session_id: str, files: List[dict]) -> None:
        embedder = Embedder()

        for file in files:
            path = file["path"]
            filename = file["filename"]

            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: get_whisper_model().transcribe(
                        path,
                        verbose=False,
                        word_timestamps=True,
                    )
                )

                segments = result.get("segments", [])
                chunks_text = self._merge_segments(segments)

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
            words = seg["text"].strip().split()
            if not current_words:
                current_start = seg["start"]
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