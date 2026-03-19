import logging
from typing import AsyncGenerator, List

from groq import AsyncGroq
from sqlalchemy import text

from app.config import settings
from app.core.embedder import Embedder
from app.db.database import AsyncSessionLocal
from app.schemas.schemas import ChatMessage

logger = logging.getLogger(__name__)

CHAT_SYSTEM = """You are an expert study assistant. Answer questions using the provided context.

Rules:
- Use ALL the context provided — it may include video transcripts, image descriptions, and text
- Be concise and clear
- If asked about a video, use the transcript and frame descriptions to answer
- Cite your source using [source_ref] after each key point
- Only say you don't have information if the context is truly empty"""

OVERVIEW_TRIGGERS = [
    "overview", "summary", "about", "what is this",
    "what is the video", "what does this cover", "explain everything",
    "give me an overview", "what was discussed"
]


class ChatService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.embedder = Embedder()

    async def stream_answer(
        self,
        session_id: str,
        question: str,
        history: List[ChatMessage],
    ) -> AsyncGenerator[str, None]:

        is_overview = any(t in question.lower() for t in OVERVIEW_TRIGGERS)

        async with AsyncSessionLocal() as db:
            if is_overview:
                result = await db.execute(
                    text("""
                        SELECT content, source_ref, modality
                        FROM chunks
                        WHERE session_id = :session_id
                        ORDER BY created_at ASC
                        LIMIT 12
                    """),
                    {"session_id": str(session_id)},
                )
            else:
                q_embedding = await self.embedder.embed(question)
                result = await db.execute(
                    text("""
                        SELECT content, source_ref, modality
                        FROM chunks
                        WHERE session_id = :session_id
                        ORDER BY embedding <=> CAST(:embedding AS vector)
                        LIMIT 8
                    """),
                    {"session_id": str(session_id), "embedding": str(q_embedding)},
                )
            top_chunks = result.fetchall()

        if not top_chunks:
            yield "I couldn't find relevant content in your study material."
            return

        context = "\n\n---\n\n".join([
            f"[{row.modality.upper()} — {row.source_ref}]\n{row.content}"
            for row in top_chunks
        ])

        messages = [{"role": "system", "content": CHAT_SYSTEM}]
        messages += [
            {"role": m.role, "content": m.content}
            for m in history[-6:]
        ]
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        })

        stream = await self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            max_tokens=800,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

        sources = [row.source_ref for row in top_chunks if row.source_ref]
        if sources:
            yield f"\n\n__sources__{','.join(sources[:3])}__end_sources__"