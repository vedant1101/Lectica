import logging
import re
from typing import List

from app.core.embedder import Embedder
from app.db.database import AsyncSessionLocal
from app.models.models import Chunk, ModalityEnum

logger = logging.getLogger(__name__)

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50


class TextPipeline:

    async def run(self, session_id: str, files: List[dict]) -> None:
        embedder = Embedder()

        for file in files:
            filename = file["filename"]
            raw_text = file.get("raw_text") or self._read_file(file["path"])

            if not raw_text or not raw_text.strip():
                logger.warning(f"Empty text for {filename}, skipping")
                continue

            try:
                cleaned = self._clean(raw_text)
                chunks = self._semantic_chunk(cleaned)

                async with AsyncSessionLocal() as db:
                    for i, chunk_text in enumerate(chunks):
                        embedding = await embedder.embed(chunk_text)
                        chunk = Chunk(
                            session_id=session_id,
                            modality=ModalityEnum.text,
                            content=chunk_text,
                            source_ref=f"{filename} · chunk {i+1}/{len(chunks)}",
                            embedding=embedding,
                            metadata_={"chunk_index": i},
                        )
                        db.add(chunk)
                    await db.commit()

                logger.info(f"Text pipeline: {len(chunks)} chunks from {filename}")

            except Exception as e:
                logger.error(f"Text pipeline failed for {filename}: {e}")
                raise

    def _read_file(self, path: str) -> str:
        if path.endswith(".pdf"):
            import fitz
            doc = fitz.open(path)
            return "\n\n".join(page.get_text() for page in doc)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _clean(self, text: str) -> str:
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    def _semantic_chunk(self, text: str) -> List[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_words: List[str] = []

        for para in paragraphs:
            words = para.split()
            if len(current_words) + len(words) > CHUNK_SIZE and current_words:
                chunks.append(" ".join(current_words))
                current_words = current_words[-CHUNK_OVERLAP:]
            current_words.extend(words)

        if current_words:
            chunks.append(" ".join(current_words))

        return chunks if chunks else [text]