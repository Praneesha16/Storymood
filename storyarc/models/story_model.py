"""Pydantic models for the API (pydantic v1)."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

import catalog


class Character(BaseModel):
    name: str = Field(..., min_length=1, max_length=40)
    trait: str = Field("", max_length=60)


class StoryRequest(BaseModel):
    theme: str = "adventure"
    feeling: str = "happy"
    age_group: str = "6-8"
    length: str = "short"
    language: str = "en"
    narrator: str = "woman"
    characters: List[Character] = Field(default_factory=list, max_items=4)
    idea: str = Field("", max_length=600)
    avoid: List[str] = Field(default_factory=list, max_items=12, description="Recent story titles not to repeat")

    @validator("theme")
    def _theme(cls, v: str) -> str:
        if not catalog.theme(v):
            raise ValueError(f"unknown theme '{v}'")
        return v

    @validator("feeling")
    def _feeling(cls, v: str) -> str:
        if not catalog.feeling(v):
            raise ValueError(f"unknown feeling '{v}'")
        return v

    @validator("age_group")
    def _age(cls, v: str) -> str:
        if not catalog.age_group(v):
            raise ValueError(f"unknown age group '{v}'")
        return v

    @validator("length")
    def _length(cls, v: str) -> str:
        if not catalog.length(v):
            raise ValueError(f"unknown length '{v}'")
        return v

    @validator("language")
    def _language(cls, v: str) -> str:
        if not catalog.language(v):
            raise ValueError(f"unknown language '{v}'")
        return v

    @validator("narrator")
    def _narrator(cls, v: str) -> str:
        if not catalog.narrator(v):
            raise ValueError(f"unknown narrator '{v}'")
        return v


class StoryMeta(BaseModel):
    theme: str
    feeling: str
    age_group: str
    length: str
    language: str
    narrator: str
    characters: List[str]
    word_count: int
    estimated_minutes: int
    provider: str
    model: str


class Paragraph(BaseModel):
    text: str
    mood: str = ""   # one of catalog.MOODS; how a narrator should read it
    scene: str = ""  # what a picture of this paragraph shows (English, visual only)


class StoryPage(BaseModel):
    """One page of the book: which paragraphs it holds and what its picture shows."""
    paragraphs: List[int]
    scene: str = ""


class StoryArt(BaseModel):
    characters: str = ""  # how the heroes look, repeated in every picture prompt for consistency
    cover: str = ""       # what the cover picture shows


class StoryResponse(BaseModel):
    id: str = ""  # the record in the family's library (empty for previews)
    title: str
    story_text: str
    meta: StoryMeta
    mood: str = ""  # overall mood, used to choose the music
    music_url: Optional[str] = None  # background track under /static/music, or None for silence
    paragraphs: List[Paragraph] = Field(default_factory=list)
    pages: List[StoryPage] = Field(default_factory=list)
    art: Optional[StoryArt] = None


class PictureReference(BaseModel):
    """A character's photo or drawing, as a data URL, so the painting takes after it. Never stored."""
    name: str = Field(..., min_length=1, max_length=40)
    image: str = Field(..., min_length=50, max_length=1_500_000, regex="^data:image/(jpeg|png|webp);base64,")


class IllustrateRequest(BaseModel):
    title: str = Field("", max_length=120)
    scene: str = Field(..., min_length=3, max_length=1200)
    characters: str = Field("", max_length=600)
    kind: str = Field("page", regex="^(page|cover)$")
    references: List[PictureReference] = Field(default_factory=list, max_items=4)
    story_id: str = Field("", max_length=64, description="Library record to attach the picture to")
    key: str = Field("", max_length=16, regex="^(|cover|page-\\d{1,2})$", description="cover or page-N")


class IllustrateResponse(BaseModel):
    image_url: str
    provider: str
    model: str


class NarrationSegment(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    mood: str = ""

    @validator("mood")
    def _mood(cls, v: str) -> str:
        if v and not catalog.mood(v):
            raise ValueError(f"unknown mood '{v}'")
        return v


class NarrationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    narrator: str = "woman"
    language: str = "en"
    voice_id: Optional[str] = Field(None, max_length=80, description="Vendor voice id (e.g. a cloned family voice); overrides narrator")
    segments: Optional[List[NarrationSegment]] = Field(
        None, max_items=300, description="Mood-tagged passages for expressive reading; when given, `text` is ignored"
    )
    music: bool = Field(True, description="Mix mood-matched background music under the voice (needs ffmpeg and tracks)")
    story_id: str = Field("", max_length=64, description="Library record to attach the recording to")

    @validator("narrator")
    def _narrator(cls, v: str) -> str:
        if not catalog.narrator(v):
            raise ValueError(f"unknown narrator '{v}'")
        return v

    @validator("language")
    def _language(cls, v: str) -> str:
        if not catalog.language(v):
            raise ValueError(f"unknown language '{v}'")
        return v


class NarrationCue(BaseModel):
    """When segment `index` is heard, in seconds from the start of the file."""
    index: int
    start: float
    end: float


class NarrationResponse(BaseModel):
    audio_url: str
    provider: str
    voice: str
    music: bool = False  # True when background music is mixed into the file
    cues: List[NarrationCue] = Field(default_factory=list)  # empty when timings are unknown (no ffmpeg)


class VoiceCloneResponse(BaseModel):
    voice_id: str
    name: str
    provider: str


class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None  # ISO code when detected; the UI may switch language on it
    provider: str


class VideoRequest(BaseModel):
    story_text: str
    title: str = ""
    language: str = "en"


class VideoResponse(BaseModel):
    provider: str
    data: Dict[str, Any]


# ---- Story vault (DynamoDB) -------------------------------------------------------------
class StoryVaultItem(BaseModel):
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    story_text: str
    audio_url: Optional[str] = None
    meta: Dict[str, Any]
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class UserStoryList(BaseModel):
    stories: List[StoryVaultItem]
