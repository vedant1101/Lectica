import asyncio
import logging
import os
import time
from typing import List

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"


async def fetch_embedding(client: httpx.AsyncClient, text: str, retries=3, delay=1):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"inputs": text}

    for attempt in range(retries):
        try:
            res = await client.post(HF_URL, headers=headers, json=payload, timeout=15)

            if res.status_code == 429:
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Rate limited. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue

            res.raise_for_status()
            data = res.json()

            # Ensure correct format
            if isinstance(data, list):
                return data[0] if isinstance(data[0], list) else data

            raise Exception("Invalid embedding format")

        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Embedding failed: {e}")
                return None


class Embedder:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def embed(self, text: str) -> List[float]:
        return await fetch_embedding(self.client, text)

    async def embed_many(self, texts: List[str]) -> List[List[float]]:
        tasks = [fetch_embedding(self.client, t) for t in texts]
        return await asyncio.gather(*tasks)