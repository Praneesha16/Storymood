"""Everything a child can pick, in one place.

The frontend renders these lists from GET /api/v1/catalog, so adding a theme, feeling,
narrator or language here is enough to make it appear in the app.

Narrator "voices" map provider name -> voice. A value may be a single voice name (used for
every language) or a dict keyed by ISO language code; a narrator is only offered in the
languages that have a voice. Vendor voice ids were chosen from
the Cartesia library for storytelling tone; swap them freely.
"""
from typing import Any, Dict, List, Optional

LANGUAGES: List[Dict[str, str]] = [
    {"code": "en", "label": "English", "native": "English", "emoji": "🌍"},
    {"code": "hi", "label": "Hindi", "native": "हिन्दी", "emoji": "🪔"},
    {"code": "te", "label": "Telugu", "native": "తెలుగు", "emoji": "🌸"},
    {"code": "ta", "label": "Tamil", "native": "தமிழ்", "emoji": "🌿"},
    {"code": "ml", "label": "Malayalam", "native": "മലയാളം", "emoji": "🥥"},
]

THEMES: List[Dict[str, str]] = [
    {"id": "adventure", "label": "Adventure", "emoji": "🗺️", "color": "coral",
     "hint": "a thrilling quest with a map, a tricky obstacle and a brave journey home"},
    {"id": "animals", "label": "Animals", "emoji": "🦁", "color": "sun",
     "hint": "talking animals with big personalities who learn something together"},
    {"id": "magic", "label": "Magic", "emoji": "🪄", "color": "grape",
     "hint": "wands, spells that go a little wrong, and a kind wizard or witch"},
    {"id": "space", "label": "Space", "emoji": "🚀", "color": "sky",
     "hint": "rockets, friendly aliens, planets with funny weather and a return to Earth"},
    {"id": "ocean", "label": "Ocean", "emoji": "🐳", "color": "mint",
     "hint": "mermaids, whales, a sunken treasure and sparkling coral reefs"},
    {"id": "dinosaurs", "label": "Dinosaurs", "emoji": "🦕", "color": "leaf",
     "hint": "gentle giant dinosaurs, a volcano that only burps, and a lost egg"},
    {"id": "funny", "label": "Silly & Funny", "emoji": "🤪", "color": "sun",
     "hint": "ridiculous mix-ups, silly sounds and a giggle on every page"},
    {"id": "friendship", "label": "Friendship", "emoji": "🤝", "color": "peach",
     "hint": "two very different friends who help each other and share"},
    {"id": "fairy_tale", "label": "Fairy Tale", "emoji": "🏰", "color": "grape",
     "hint": "a castle, a clever hero, a tiny bit of enchantment and a happy ending"},
    {"id": "bedtime", "label": "Bedtime", "emoji": "🌙", "color": "night",
     "hint": "a soft, slow, cosy story that gets sleepier towards the end"},
]

FEELINGS: List[Dict[str, str]] = [
    {"id": "happy", "label": "Happy", "emoji": "😊", "hint": "cheerful, sunny and full of smiles", "mood": "happy"},
    {"id": "exciting", "label": "Exciting", "emoji": "⚡", "hint": "fast, surprising and full of wow moments", "mood": "excited"},
    {"id": "calm", "label": "Calm", "emoji": "😌", "hint": "gentle, soothing and slow", "mood": "calm"},
    {"id": "silly", "label": "Silly", "emoji": "🤭", "hint": "goofy, playful and giggly", "mood": "silly"},
    {"id": "magical", "label": "Magical", "emoji": "✨", "hint": "wonder-filled, sparkly and dreamy", "mood": "magical"},
    {"id": "brave", "label": "Brave", "emoji": "🦸", "hint": "courageous, kind and confident", "mood": "brave"},
]

# Moods tag the whole story (to pick background music) and each paragraph (so the narrator
# changes delivery). "emotion" is the Cartesia Sonic-3 emotion name the voice adapter sends;
# "like" lists similar moods to borrow music from when a mood has no track of its own.
MOODS: List[Dict[str, Any]] = [
    {"id": "happy", "label": "Happy", "emoji": "😊", "emotion": "happy", "like": ["silly", "tender", "excited"],
     "hint": "cheerful, sunny, smiling"},
    {"id": "excited", "label": "Excited", "emoji": "⚡", "emotion": "excited", "like": ["happy", "brave"],
     "hint": "fast, surprising, wow moments"},
    {"id": "calm", "label": "Calm", "emoji": "😌", "emotion": "calm", "like": ["sleepy", "tender"],
     "hint": "gentle, soothing, slow"},
    {"id": "silly", "label": "Silly", "emoji": "🤪", "emotion": "enthusiastic", "like": ["happy", "excited"],
     "hint": "goofy, giggly, playful"},
    {"id": "magical", "label": "Magical", "emoji": "✨", "emotion": "amazed", "like": ["mysterious", "calm"],
     "hint": "wonder, sparkle, dreams"},
    {"id": "brave", "label": "Brave", "emoji": "🦸", "emotion": "determined", "like": ["excited", "happy"],
     "hint": "courage, determination, standing tall"},
    {"id": "mysterious", "label": "Mysterious", "emoji": "🔍", "emotion": "mysterious", "like": ["magical", "calm"],
     "hint": "puzzles, hidden things, quiet suspense"},
    {"id": "sleepy", "label": "Sleepy", "emoji": "🌙", "emotion": "calm", "like": ["calm", "tender"],
     "hint": "bedtime, yawns, drifting off"},
    {"id": "tender", "label": "Tender", "emoji": "🥰", "emotion": "affectionate", "like": ["calm", "happy"],
     "hint": "warm, loving, friendship, kindness"},
    {"id": "worried", "label": "A little worried", "emoji": "😟", "emotion": "anxious", "like": ["mysterious", "calm"],
     "hint": "the small problem in the middle, never scary"},
]
MOOD_IDS: List[str] = [m["id"] for m in MOODS]

AGE_GROUPS: List[Dict[str, str]] = [
    {"id": "3-5", "label": "3 to 5", "emoji": "🧸",
     "guidance": "very short sentences, repetition, simple words, lots of sounds like 'whoosh' and 'boing'"},
    {"id": "6-8", "label": "6 to 8", "emoji": "🎒",
     "guidance": "clear sentences, a small problem to solve, playful dialogue, a gentle lesson"},
    {"id": "9-12", "label": "9 to 12", "emoji": "🔭",
     "guidance": "richer vocabulary, a twist, humour and characters with real feelings"},
]

LENGTHS: List[Dict[str, Any]] = [
    {"id": "short", "label": "Short", "emoji": "🐣", "minutes": "2 min", "words": 250},
    {"id": "medium", "label": "Medium", "emoji": "🐥", "minutes": "4 min", "words": 500},
    {"id": "long", "label": "Long", "emoji": "🦉", "minutes": "7 min", "words": 900},
]

NARRATORS: List[Dict[str, Any]] = [
    # A narrator is offered in a language only when the active TTS provider has a voice for it
    # (no fallback to English). English has true child and elderly voices; the Indian languages
    # have adult voices only, so the grandparents there are the warmest adults. Malayalam has two.
    {
        "id": "girl", "label": "Little Girl", "emoji": "👧", "blurb": "Bright and giggly",
        "speed": 1.0,
        "pitch": {"en": 1.15},  # no real child voices exist; the mixer raises an adult voice (chosen by ear)
        "style": "A cheerful little girl reading a story to her best friend. Bright, bouncy, full of wonder.",
        "voices": {
            "cartesia": {
                "en": "32b3f3c5-7171-46aa-abe7-b598964aa793",  # Daisy - Reading Girl
            },
            "openai": "coral",
        },
    },
    {
        "id": "boy", "label": "Little Boy", "emoji": "👦", "blurb": "Bouncy and brave",
        "speed": 1.0,
        "pitch": {"en": 1.10},
        "style": "An excited little boy telling a story to his friends. Energetic, playful, dramatic.",
        "voices": {
            "cartesia": {
                "en": "c961b81c-a935-4c17-bfb3-ba2239de8c2f",  # Kyle - Approachable Friend, raised 10% by the mixer
            },
            "openai": "ballad",
        },
    },
    {
        "id": "woman", "label": "Kind Lady", "emoji": "👩", "blurb": "Warm and clear",
        "speed": 0.95,
        "style": "A warm, kind woman reading aloud to children. Clear, expressive, smiling.",
        "voices": {
            "cartesia": {
                "en": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b",  # Tessa - Kind Companion
                "hi": "4459a9a5-69d6-4680-b970-e13dc51845b6",  # Siya - Bright Conversationalist
                "te": "062c17da-6ab6-4ecc-9f8a-d2a3dace8003",  # Deepthi - Solution Navigator
                "ta": "7f98e662-142d-41ba-89a2-12452640ce6d",  # Lakshmi - Everyday Voice
                "ml": "b426013c-002b-4e89-8874-8cd20b68373a",  # Latha - Friendly Host
            },
            "openai": "nova",
        },
    },
    {
        "id": "man", "label": "Friendly Man", "emoji": "👨", "blurb": "Calm and strong",
        "speed": 0.95,
        "style": "A friendly, warm man reading a story to children. Calm, clear, with a smile in the voice.",
        "voices": {
            "cartesia": {
                "en": "0834f3df-e650-4766-a20c-5a93a43aa6e3",  # Leo - Genuine Companion
                "hi": "7e8cb11d-37af-476b-ab8f-25da99b18644",  # Anuj - Engaging Narrator
                "te": "38bded0a-3ab4-42d1-8e47-2e0b6b10ced9",  # Vikram - Folk Narrator
                "ta": "19f28c21-ae34-499f-b64a-f7b09cd9b516",  # Karthik - Customer Assistant
                "ml": "374b80da-e622-4dfc-90f6-1eeb13d331c9",  # Vijay - Comfort Voice
            },
            "openai": "echo",
        },
    },
    {
        "id": "grandma", "label": "Cozy Grandma", "emoji": "👵", "blurb": "Soft and gentle",
        "speed": 0.9,
        "pitch": {"en": 0.92},
        "style": "A warm, loving grandmother reading a story to a small child. Gentle, expressive, unhurried.",
        "voices": {
            "cartesia": {
                "en": "bf991597-6c13-47e4-8411-91ec2de5c466",  # Carol - Task Coach, lowered 8% by the mixer
            },
            "openai": "marin",
        },
    },
    {
        "id": "grandpa", "label": "Jolly Grandpa", "emoji": "👴", "blurb": "Deep and twinkly",
        "speed": 0.92,
        "style": "A jolly grandfather telling a tale by the fire. Deep, warm, a chuckle in the voice.",
        "voices": {
            "cartesia": {
                "en": "0ad65e7f-006c-47cf-bd31-52279d487913",  # Rupert - Caring Dad (mature)
            },
            "openai": "cedar",
        },
    },
]


def _by_id(items: List[Dict[str, Any]], key: str, value: str) -> Optional[Dict[str, Any]]:
    return next((item for item in items if item[key] == value), None)


def theme(theme_id: str) -> Optional[Dict[str, Any]]:
    return _by_id(THEMES, "id", theme_id)


def feeling(feeling_id: str) -> Optional[Dict[str, Any]]:
    return _by_id(FEELINGS, "id", feeling_id)


def age_group(age_id: str) -> Optional[Dict[str, Any]]:
    return _by_id(AGE_GROUPS, "id", age_id)


def length(length_id: str) -> Optional[Dict[str, Any]]:
    return _by_id(LENGTHS, "id", length_id)


def narrator(narrator_id: str) -> Optional[Dict[str, Any]]:
    return _by_id(NARRATORS, "id", narrator_id)


def language(code: str) -> Optional[Dict[str, str]]:
    return _by_id(LANGUAGES, "code", code)


def mood(mood_id: str) -> Optional[Dict[str, Any]]:
    return _by_id(MOODS, "id", mood_id)


def default_mood(feeling_id: str) -> str:
    """The mood a story falls back to when the writer did not tag one."""
    entry = feeling(feeling_id)
    return entry.get("mood", "happy") if entry else "happy"


def resolve_voice(narrator_id: str, provider_name: str, lang: str) -> Optional[str]:
    """Vendor voice id for a narrator in a language; None when the provider has no such voice."""
    entry = narrator(narrator_id)
    if not entry:
        return None
    voices = entry["voices"].get(provider_name)
    if isinstance(voices, dict):
        return voices.get(lang)
    return voices  # a single name works in every language (OpenAI)


def resolve_pitch(narrator_id: str, lang: str) -> float:
    """Pitch factor the mixer applies (1.0 = as recorded, 1.15 = younger, 0.9 = older). Per language or one value."""
    entry = narrator(narrator_id) or {}
    pitch = entry.get("pitch", 1.0)
    if isinstance(pitch, dict):
        return float(pitch.get(lang, 1.0))
    return float(pitch)


def narrator_languages(narrator_id: str, provider_name: str) -> List[str]:
    """Languages the narrator can read with this provider."""
    return [l["code"] for l in LANGUAGES if resolve_voice(narrator_id, provider_name, l["code"])]


def public(tts_provider: str = "cartesia") -> Dict[str, Any]:
    """Catalog for the frontend: vendor voice ids are stripped out; each narrator lists its languages."""
    return {
        "languages": LANGUAGES,
        "themes": THEMES,
        "feelings": FEELINGS,
        "age_groups": AGE_GROUPS,
        "lengths": [{k: v for k, v in item.items() if k != "words"} for item in LENGTHS],
        "narrators": [
            {**{k: v for k, v in item.items() if k not in ("voices", "style", "speed", "pitch")},
             "languages": narrator_languages(item["id"], tts_provider)}
            for item in NARRATORS
        ],
        "moods": [{k: v for k, v in item.items() if k in ("id", "label", "emoji")} for item in MOODS],
    }
