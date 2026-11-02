"""Abstract interfaces every provider adapter implements.

A capability (LLM, TTS, STT, video) is a small base class. Concrete adapters live in
sibling modules and are selected by name in providers/registry.py. Services depend only
on these interfaces, so a vendor swap is a one-line change in .env.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class ProviderError(Exception):
    """A failure with a message safe to show in the UI."""


@dataclass
class VoiceSpec:
    """Vendor-agnostic description of how a narrator should sound.

    voice: the vendor's voice id or name (resolved from catalog.py).
    speed: 1.0 is normal. Adapters clamp to their own supported range.
    style: free-text delivery hint for vendors that accept one (OpenAI `instructions`).
    """

    voice: str
    speed: float = 1.0
    style: str = ""


@dataclass
class Transcript:
    text: str
    language: Optional[str] = None  # ISO-639-1 code when the vendor reports one


class LLMProvider(ABC):
    name: str = ""
    model: str = ""

    @abstractmethod
    async def generate(
        self,
        system: str,
        prompt: str,
        *,
        max_tokens: int = 4000,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Return the model's text. With json_schema, the text is a JSON document matching it."""


class TTSProvider(ABC):
    name: str = ""
    model: str = ""
    audio_format: str = "mp3"  # services concatenate chunks, which only works for mp3
    max_chars: int = 2000      # longest transcript sent in one request
    supports_cloning: bool = False

    @abstractmethod
    async def synthesize(self, text: str, voice: VoiceSpec, language: str) -> bytes:
        """Return encoded audio bytes for `text` in `language` (ISO-639-1)."""

    async def clone_voice(self, audio: bytes, filename: str, content_type: str, name: str, language: str) -> str:
        """Create a voice from a short recording and return its vendor voice id. Optional."""
        raise ProviderError(f"The {self.name or 'current'} voice provider cannot clone voices.")


class STTProvider(ABC):
    name: str = ""
    model: str = ""

    @abstractmethod
    async def transcribe(
        self,
        audio: bytes,
        filename: str,
        content_type: str,
        language: Optional[str] = None,
    ) -> Transcript:
        """Transcribe an uploaded recording. `language` is a hint; None means auto-detect."""


class VideoProvider(ABC):
    name: str = ""
    enabled: bool = True

    @abstractmethod
    async def generate(self, story_text: str, title: str, language: str) -> Dict[str, Any]:
        """Return a vendor-shaped payload describing the produced video or scenes."""
