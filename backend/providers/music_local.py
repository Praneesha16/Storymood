"""Background music from files on disk. No API, no cost.

Drop tracks into backend/static/music named after a mood from catalog.MOODS, for example
    happy-sunny-day.mp3   calm_river.mp3   sleepy.m4a   excited-2.ogg
The part before the first "-", "_" or "." is the mood. Several files per mood are fine; one is
picked at random each story. Files are re-scanned on every request, so adding one needs no restart.
"""
import os
import random
import re
from typing import Dict, List, Optional
from urllib.parse import quote, unquote

import config
from providers.base import MusicProvider

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".ogg", ".oga", ".wav", ".flac", ".webm"}


class LocalMusic(MusicProvider):
    name = "local"

    def __init__(self) -> None:
        self.folder = config.MUSIC_FILES_DIR
        os.makedirs(self.folder, exist_ok=True)

    def _scan(self) -> Dict[str, List[str]]:
        by_mood: Dict[str, List[str]] = {}
        for filename in sorted(os.listdir(self.folder)):
            stem, ext = os.path.splitext(filename)
            if ext.lower() not in AUDIO_EXTENSIONS:
                continue
            mood = re.split(r"[-_. ]", stem, maxsplit=1)[0].strip().lower()
            if mood:
                by_mood.setdefault(mood, []).append(filename)
        return by_mood

    def tracks(self) -> Dict[str, int]:
        return {mood: len(files) for mood, files in self._scan().items()}

    def local_path(self, url: str) -> Optional[str]:
        path = os.path.join(self.folder, unquote(url.rsplit("/", 1)[-1]))
        return path if os.path.isfile(path) else None

    async def pick(self, mood: str, alternatives: List[str]) -> Optional[str]:
        by_mood = self._scan()
        for candidate in [mood, *alternatives]:
            files = by_mood.get(candidate)
            if files:
                return f"{config.MUSIC_FILES_URL_PATH}/{quote(random.choice(files))}"
        return None
