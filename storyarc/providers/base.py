"""Abstract interfaces every provider adapter implements.

A capability (LLM, TTS, STT, video, music) is a small base class. Concrete adapters live in
sibling modules and are selected by name in providers/registry.py. Services depend only
on these interfaces, so a vendor swap is a one-line change in .env.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


class ProviderError(Exception):
    """A failure with a message safe to show in the UI."""


@dataclass
class VoiceSpec:
    """Vendor-agnostic description of how a narrator should sound.

    voice: the vendor's voice id or name (resolved from catalog.py).
    speed: 1.0 is normal. Adapters clamp to their own supported range.
    style: free-text delivery hint for vendors that accept one (OpenAI `instructions`).
    emotion: how this passage should be read, as a Cartesia emotion name (see catalog.MOODS).
             Empty means let the voice follow the text. Adapters that cannot steer emotion ignore it.
    """

    voice: str
    speed: float = 1.0
    style: str = ""
    emotion: str = ""


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


class MusicProvider(ABC):
    """Background music for a story. Today the only adapter serves files from disk; a generative
    vendor (Lyria, Stable Audio, ElevenLabs Music) would implement `pick` by creating a track."""

    name: str = ""
    enabled: bool = True

    @abstractmethod
    async def pick(self, mood: str, alternatives: List[str]) -> Optional[str]:
        """URL of a track for `mood`, trying `alternatives` in order when none fits. None means silence."""

    def tracks(self) -> Dict[str, int]:
        """How many tracks exist per mood, for the /music status route. Optional."""
        return {}

    def local_path(self, url: str) -> Optional[str]:
        """Where the mixer can read the track that `pick` returned; None if it is not on disk."""
        return None


class ImageProvider(ABC):
    """Paints one picture from a text description."""

    name: str = ""
    model: str = ""
    enabled: bool = True

    @abstractmethod
    async def generate(
        self, prompt: str, *, portrait: bool = True, references: List[Tuple[bytes, str]] = ()
    ) -> Tuple[bytes, str]:
        """Return (image bytes, file extension such as 'webp' or 'png').

        references: optional (bytes, mime type) pictures the result should take after, in the order
        the prompt refers to them ("picture 1", "picture 2", ...).
        """


class StoreProvider(ABC):
    """Where story records and family accounts live (JSON files locally, DynamoDB in production)."""

    name: str = ""

    @abstractmethod
    async def put_story(self, record: Dict[str, Any]) -> None: ...

    @abstractmethod
    async def get_story(self, story_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    async def update_story(self, story_id: str, **fields: Any) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    async def delete_story(self, story_id: str) -> None: ...

    @abstractmethod
    async def stories_by_owner(self, owner_id: str) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def stories_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    async def put_user(self, record: Dict[str, Any]) -> None: ...


class FileStore(ABC):
    """Where narration and pictures are kept and served from (local static folder, or S3 + CloudFront)."""

    name: str = ""

    @abstractmethod
    async def save(self, kind: str, filename: str, data: bytes, content_type: str) -> str:
        """Store bytes under `kind` ("audio" or "images") and return the URL the browser should use."""


class VideoProvider(ABC):
    name: str = ""
    enabled: bool = True

    @abstractmethod
    async def generate(self, story_text: str, title: str, language: str) -> Dict[str, Any]:
        """Return a vendor-shaped payload describing the produced video or scenes."""
