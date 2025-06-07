from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class StoryType(str, Enum):
    ADVENTURE = "Adventure"
    MORAL = "Moral"
    COMEDY = "Comedy"
    SCIFI = "Sci-Fi"
    FANTASY = "Fantasy"
    HISTORICAL = "Historical"
    MYSTERY = "Mystery"
    FAIRY_TALE = "Fairy Tale"
    DRAMA = "Drama"

class Mood(str, Enum):
    SOOTHING = "Soothing"
    INTENSE = "Intense"
    JOYFUL = "Joyful"
    HEALING = "Healing"
    INSPIRING = "Inspiring"
    SUSPENSEFUL = "Suspenseful"
    MAGICAL = "Magical"

class Language(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    TELUGU = "Telugu"

class NarratorStyle(str, Enum):
    WISE_GRANDPARENT = "Wise Grandparent"
    CHILDS_VOICE = "Child's Voice"
    CELEBRITY = "Celebrity-style"
    NEUTRAL_AI = "Neutral AI"
    INDIAN_ENGLISH = "Indian English"
    SELF = "Self"

class Character(BaseModel):
    name: str
    age: int
    trait: str

class StoryGenerationRequest(BaseModel):
    story_type: StoryType
    mood: Mood
    narrator_style: NarratorStyle
    language: Language = Language.ENGLISH
    custom_characters: Optional[List[Character]] = Field(default=[])
    private_prompt: Optional[str] = None

class StoryMetadata(BaseModel):
    estimated_duration: str
    story_type: StoryType
    mood: Mood
    narrator_style: NarratorStyle
    language: Language
    characters: List[str]

class StoryGenerationResponse(BaseModel):
    story_text: str
    meta: StoryMetadata

class NarrationRequest(BaseModel):
    story_text: str
    narrator_style: NarratorStyle
    language: Language = Language.ENGLISH

class NarrationResponse(BaseModel):
    """
    Response model for story narration.
    audio_url: URL path to the generated audio file on the server
    """
    audio_url: str

class StoryVaultItem(BaseModel):
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    story_text: str
    audio_url: Optional[str] = None
    meta: Dict[str, Any]
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class UserStoryList(BaseModel):
    stories: List[StoryVaultItem]
