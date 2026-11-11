"""Placeholder video adapter. Keeps the video capability wired while no vendor is chosen.

To enable video: write providers/<vendor>_video.py extending VideoProvider, register it in
providers/registry.py under "video", and set VIDEO_PROVIDER=<vendor> in .env.
"""
from typing import Any, Dict

from providers.base import ProviderError, VideoProvider


class DisabledVideo(VideoProvider):
    name = "none"
    enabled = False

    async def generate(self, story_text: str, title: str, language: str) -> Dict[str, Any]:
        raise ProviderError("Video generation is not set up yet. Set VIDEO_PROVIDER in backend/.env.")
