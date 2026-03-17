import logging
from typing import AsyncGenerator, List

import anthropic
from sqlalchemy import text

from app.config import settings
from app.core.embedder import Embedder
from app.db.database import AsyncSessionLocal
from app.schemas.schemas import ChatMessage

logger = logging.getLogger(__name__)

CHAT_SYSTEM = """You are an expert study assistant. Answer questions using ONLY the provided context.

Rules:
- Be concise and clear
- Cite your source using [source_ref] format after each key point
- If the answer is not in the context say "I don't have information about that in your study material"
- Do NOT make up information"""


class ChatService:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.embedder = Embedder()

    async def stream_answer(
        self,
        session_id: str,
        question: str,
        history: List[ChatMessage],
    ) -> AsyncGenerator[str, None]:

        # 1. Embed the question
        q_embedding = await self.embedder.embed(question)

        # 2. Vector similarity search
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text("""
                    SELECT content, source_ref, modality
                    FROM chunks
                    WHERE session_id = :session_id
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT 5
                """),
                {"session_id": str(session_id), "embedding": str(q_embedding)},
            )
            top_chunks = result.fetchall()

        if not top_chunks:
            yield "I couldn't find relevant content in your study material."
            return

        # 3. Build context
        context = "\n\n---\n\n".join([
            f"[{row.modality.upper()} — {row.source_ref}]\n{row.content}"
            for row in top_chunks
        ])

        # 4. Build messages
        messages = [
            {"role": m.role, "content": m.content}
            for m in history[-6:]
        ]
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        })

        # 5. Stream response
        async with self.client.messages.stream(
            model=settings.CLAUDE_FAST_MODEL,
            max_tokens=800,
            system=CHAT_SYSTEM,
            messages=messages,
        ) as stream:
            async for text_chunk in stream.text_stream:
                yield text_chunk

        # 6. Yield sources
        sources = [row.source_ref for row in top_chunks if row.source_ref]
        if sources:
            yield f"\n\n__sources__{','.join(sources[:3])}__end_sources__"