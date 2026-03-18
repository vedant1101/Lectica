import base64
import logging
from pathlib import Path
from typing import List

import anthropic

from app.config import settings
from app.core.embedder import Embedder
from app.db.database import AsyncSessionLocal
from app.models.models import Chunk, ModalityEnum

logger = logging.getLogger(__name__)

VISION_PROMPT = """You are analyzing an educational image (slide, diagram, textbook page, or whiteboard).

Extract ALL educational content visible in this image:
1. All text verbatim (headings, bullet points, body text, captions)
2. Describe any diagrams, charts, or figures and what they show
3. Any formulas, equations, or code snippets

Format your response as clean, structured text that captures the full educational content.
Do NOT add commentary — only extract what is present in the image."""


class VisionPipeline:

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def run(self, session_id: str, files: List[dict]) -> None:
        embedder = Embedder()

        for file in files:
            path = file["path"]
            filename = file["filename"]

            try:
                with open(path, "rb") as f:
                    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

                media_type = self._get_media_type(filename)

                response = await self.client.messages.create(
                    model=settings.CLAUDE_VISION_MODEL,
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {"type": "text", "text": VISION_PROMPT},
                        ],
                    }],
                )

                extracted_text = response.content[0].text
                embedding = await embedder.embed(extracted_text)

                async with AsyncSessionLocal() as db:
                    chunk = Chunk(
                        session_id=session_id,
                        modality=ModalityEnum.image,
                        content=extracted_text,
                        source_ref=filename,
                        embedding=embedding,
                        metadata_={"original_file": filename},
                    )
                    db.add(chunk)
                    await db.commit()

                logger.info(f"Vision pipeline: extracted from {filename}")

            except Exception as e:
                logger.error(f"Vision pipeline failed for {filename}: {e}")
                raise

    def _get_media_type(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        return {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(ext, "image/jpeg")