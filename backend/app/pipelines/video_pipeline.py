import asyncio
import logging
import os
import subprocess
import tempfile
from typing import List

from app.pipelines.audio_pipeline import AudioPipeline
from app.pipelines.vision_pipeline import VisionPipeline

logger = logging.getLogger(__name__)

KEYFRAME_THRESHOLD = 0.4
MAX_KEYFRAMES = 20


class VideoPipeline:

    def __init__(self):
        self.audio_pipeline = AudioPipeline()
        self.vision_pipeline = VisionPipeline()

    async def run(self, session_id: str, files: List[dict]) -> None:
        for file in files:
            path = file["path"]
            filename = file["filename"]

            with tempfile.TemporaryDirectory() as tmpdir:
                try:
                    # 1. Extract audio
                    audio_path = os.path.join(tmpdir, "audio.wav")
                    await self._extract_audio(path, audio_path)

                    # 2. Extract keyframes
                    frames_dir = os.path.join(tmpdir, "frames")
                    os.makedirs(frames_dir, exist_ok=True)
                    await self._extract_keyframes(path, frames_dir)

                    # 3. Run audio + vision in parallel
                    audio_files = [{
                        "filename": f"{filename}_audio.wav",
                        "path": audio_path
                    }]
                    frame_files = [
                        {
                            "filename": f"{filename}_frame_{i:04d}.jpg",
                            "path": os.path.join(frames_dir, f),
                        }
                        for i, f in enumerate(
                            sorted(os.listdir(frames_dir))[:MAX_KEYFRAMES]
                        )
                    ]

                    await asyncio.gather(
                        self.audio_pipeline.run(session_id, audio_files),
                        self.vision_pipeline.run(session_id, frame_files),
                    )

                    logger.info(f"Video pipeline done: {filename}")

                except Exception as e:
                    logger.error(f"Video pipeline failed for {filename}: {e}")
                    raise

    async def _extract_audio(self, video_path: str, output_path: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
                 "-ar", "16000", "-ac", "1", output_path, "-y"],
                check=True, capture_output=True,
            )
        )

    async def _extract_keyframes(self, video_path: str, frames_dir: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                [
                    "ffmpeg", "-i", video_path,
                    "-vf", f"select='gt(scene,{KEYFRAME_THRESHOLD})',scale=1280:-1",
                    "-vsync", "vfr", "-q:v", "2",
                    os.path.join(frames_dir, "frame_%04d.jpg"), "-y",
                ],
                check=True, capture_output=True,
            )
        )