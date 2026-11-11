"""No background music. Select with MUSIC_PROVIDER=none."""
from typing import List, Optional

from providers.base import MusicProvider


class DisabledMusic(MusicProvider):
    name = "none"
    enabled = False

    async def pick(self, mood: str, alternatives: List[str]) -> Optional[str]:
        return None
