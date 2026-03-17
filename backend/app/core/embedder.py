import asyncio
import logging
from typing import List

from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


class Embedder:
    async def embed(self, text: str) -> List[float]:
        loop = asyncio.get_event_loop()
        vector = await loop.run_in_executor(
            None,
            lambda: get_model().encode(text, normalize_embeddings=True).tolist()
        )
        return vector

    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        loop = asyncio.get_event_loop()
        vectors = await loop.run_in_executor(
            None,
            lambda: get_model().encode(texts, normalize_embeddings=True).tolist()
        )
        return vectors