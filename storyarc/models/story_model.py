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
    narrator: str = "grandma"
    characters: List[Character] = Field(default_factory=list, max_items=4)
    idea: str = Field("", max_length=600)

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


class StoryResponse(BaseModel):
    title: str
    story_text: str
    meta: StoryMeta


class NarrationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    narrator: str = "grandma"
    language: str = "en"
    voice_id: Optional[str] = Field(None, max_length=80, description="Vendor voice id (e.g. a cloned family voice); overrides narrator")

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


class NarrationResponse(BaseModel):
    audio_url: str
    provider: str
    voice: str


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
