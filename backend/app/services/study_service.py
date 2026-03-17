import json
import logging
from typing import List

import anthropic
from sqlalchemy import select

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.models.models import Chunk, Flashcard

logger = logging.getLogger(__name__)

FLASHCARD_PROMPT = """You are an expert tutor. Given the following study content, generate {n} high-quality flashcards.

Rules:
- Each question should test a single, clear concept
- Answers should be concise (1-3 sentences)
- Cover the most important concepts

Respond ONLY with a valid JSON array, no markdown:
[
  {{"question": "...", "answer": "..."}},
  ...
]

Content:
{content}"""

QUIZ_PROMPT = """Generate {n} multiple-choice quiz questions from this content.

Rules:
- 4 options each, exactly one correct
- Include a brief explanation for the correct answer

Respond ONLY with valid JSON, no markdown:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "explanation": "..."
  }}
]

Content:
{content}"""

SUMMARY_PROMPT = """Summarize the following study content.

Respond ONLY with valid JSON, no markdown:
{{
  "title": "short descriptive title",
  "key_concepts": ["concept 1", "concept 2"],
  "summary": "2-3 paragraph summary"
}}

Content:
{content}"""


class StudyService:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_all(self, session_id: str) -> None:
        chunks = await self._get_chunks(session_id)
        if not chunks:
            return
        combined = self._combine_chunks(chunks)
        n_cards = min(15, max(5, len(chunks) * 2))
        await self._generate_flashcards(session_id, combined, n_cards)

    async def generate_quiz(self, session_id: str, n: int = 5) -> List[dict]:
        chunks = await self._get_chunks(session_id)
        combined = self._combine_chunks(chunks)
        return await self._call_claude_json(QUIZ_PROMPT.format(n=n, content=combined))

    async def generate_summary(self, session_id: str) -> dict:
        chunks = await self._get_chunks(session_id)
        combined = self._combine_chunks(chunks)
        return await self._call_claude_json(SUMMARY_PROMPT.format(content=combined))

    async def _generate_flashcards(self, session_id: str, content: str, n: int):
        cards = await self._call_claude_json(
            FLASHCARD_PROMPT.format(n=n, content=content)
        )
        async with AsyncSessionLocal() as db:
            for card in cards:
                db.add(Flashcard(
                    session_id=session_id,
                    question=card["question"],
                    answer=card["answer"],
                ))
            await db.commit()

    async def _call_claude_json(self, prompt: str):
        response = await self.client.messages.create(
            model=settings.CLAUDE_FAST_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    async def _get_chunks(self, session_id: str) -> List[Chunk]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Chunk).where(Chunk.session_id == session_id)
            )
            return result.scalars().all()

    def _combine_chunks(self, chunks: List[Chunk], max_words: int = 3000) -> str:
        parts = []
        total = 0
        for c in chunks:
            words = c.content.split()
            if total + len(words) > max_words:
                break
            parts.append(c.content)
            total += len(words)
        return "\n\n".join(parts)