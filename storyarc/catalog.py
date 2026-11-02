"""Everything a child can pick, in one place.

The frontend renders these lists from GET /api/v1/catalog, so adding a theme, feeling,
narrator or language here is enough to make it appear in the app.

Narrator "voices" map provider name -> voice. A value may be a single voice name (used for
every language) or a dict keyed by ISO language code. Vendor voice ids were chosen from
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
    {"id": "happy", "label": "Happy", "emoji": "😊", "hint": "cheerful, sunny and full of smiles"},
    {"id": "exciting", "label": "Exciting", "emoji": "⚡", "hint": "fast, surprising and full of wow moments"},
    {"id": "calm", "label": "Calm", "emoji": "😌", "hint": "gentle, soothing and slow"},
    {"id": "silly", "label": "Silly", "emoji": "🤭", "hint": "goofy, playful and giggly"},
    {"id": "magical", "label": "Magical", "emoji": "✨", "hint": "wonder-filled, sparkly and dreamy"},
    {"id": "brave", "label": "Brave", "emoji": "🦸", "hint": "courageous, kind and confident"},
]

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
    {
        "id": "grandma", "label": "Cozy Grandma", "emoji": "👵", "blurb": "Warm and gentle",
        "speed": 0.9,
        "style": "A warm, loving grandmother reading a story to a small child. Gentle, expressive, unhurried.",
        "voices": {
            "cartesia": {
                "en": "a2364c9d-1fe3-4553-9eff-100c4fe5ffc8",  # Marge - Seasoned Grace
                "hi": "f91ab3e6-5071-4e15-b016-cde6f2bcd222",  # Aadhya - Soother
                "ta": "d4470f50-295e-4e11-82a2-158d45bf6abc",  # Anitha - Warm Guide
                "te": "cf061d8b-a752-4865-81a2-57570a6e0565",  # Ramya - Graceful Host
                "ml": "b426013c-002b-4e89-8874-8cd20b68373a",  # Latha - Friendly Host
            },
            "openai": "marin",
        },
    },
    {
        "id": "grandpa", "label": "Jolly Grandpa", "emoji": "👴", "blurb": "Deep and twinkly",
        "speed": 0.95,
        "style": "A jolly grandfather telling a tale by the fire. Deep, warm, a chuckle in the voice.",
        "voices": {
            "cartesia": {
                "en": "c99d36f3-5ffd-4253-803a-535c1bc9c306",  # Griffin - Narrator
                "hi": "9b953e7b-86a8-42f0-b625-1434fb15392b",  # Neeraj - Tour Guide
                "ta": "d2870b91-1b4c-47ab-81a8-3718d8e9c222",  # Arun - Lively Voice
                "te": "38bded0a-3ab4-42d1-8e47-2e0b6b10ced9",  # Vikram - Folk Narrator
                "ml": "374b80da-e622-4dfc-90f6-1eeb13d331c9",  # Vijay - Comfort Voice
            },
            "openai": "cedar",
        },
    },
    {
        "id": "pal", "label": "Playful Pal", "emoji": "🧒", "blurb": "Bouncy and fun",
        "speed": 1.05,
        "style": "An excited, playful best friend telling a story. Bright, bouncy, lots of energy.",
        "voices": {
            "cartesia": {
                "en": "2d5b8c3a-116c-4741-acaf-ba4fa289eba2",  # Benji - Joyful Spirit
                "hi": "faf0731e-dfb9-4cfc-8119-259a79b27e12",  # Riya - College Roommate
                "ta": "7f98e662-142d-41ba-89a2-12452640ce6d",  # Lakshmi - Everyday Voice
                "te": "ebecd063-10f4-422e-a8ff-556ce5c4d4e4",  # Pavan - Bright Voice
                "ml": "374b80da-e622-4dfc-90f6-1eeb13d331c9",  # Vijay - Comfort Voice
            },
            "openai": "coral",
        },
    },
    {
        "id": "fairy", "label": "Sparkle Fairy", "emoji": "🧚", "blurb": "Light and lively",
        "speed": 1.0,
        "style": "A sparkly, lively fairy narrator full of wonder. Light, musical, expressive.",
        "voices": {
            "cartesia": {
                "en": "a33f7a4c-100f-41cf-a1fd-5822e8fc253f",  # Lauren - Lively Narrator
                "hi": "4459a9a5-69d6-4680-b970-e13dc51845b6",  # Siya - Bright Conversationalist
                "ta": "25d2c432-139c-4035-bfd6-9baaabcdd006",  # Kavya - Warm Presence
                "te": "07bc462a-c644-49f1-baf7-82d5599131be",  # Sindhu - Conversational Partner
                "ml": "b426013c-002b-4e89-8874-8cd20b68373a",  # Latha - Friendly Host
            },
            "openai": "nova",
        },
    },
    {
        "id": "whisper", "label": "Sleepy Whisper", "emoji": "🌙", "blurb": "Soft for bedtime",
        "speed": 0.85,
        "style": "A soft, slow, soothing bedtime whisper. Calm and dreamy, getting gentler at the end.",
        "voices": {
            "cartesia": {
                "en": "320f7211-3dc3-4292-89b1-3661e8cac27c",  # Evelyn - Peaceful Whisper
                "hi": "209d9a43-03eb-40d8-a7b7-51a6d54c052f",  # Anita - Meditation Guide
                "ta": "fb7d8d97-9730-4165-bd79-36b5ce61b5f2",  # Janani - Calm Professional
                "te": "330c4fa0-1da3-4c55-8e97-951bfd724e20",  # Sarika - Calm Spirit
                "ml": "b426013c-002b-4e89-8874-8cd20b68373a",  # Latha - Friendly Host
            },
            "openai": "sage",
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


def resolve_voice(narrator_id: str, provider_name: str, lang: str) -> Optional[str]:
    """Vendor voice id for a narrator in a language, falling back to English."""
    entry = narrator(narrator_id)
    if not entry:
        return None
    voices = entry["voices"].get(provider_name)
    if isinstance(voices, dict):
        return voices.get(lang) or voices.get("en")
    return voices


def public() -> Dict[str, Any]:
    """Catalog for the frontend: vendor voice ids are stripped out."""
    return {
        "languages": LANGUAGES,
        "themes": THEMES,
        "feelings": FEELINGS,
        "age_groups": AGE_GROUPS,
        "lengths": [{k: v for k, v in item.items() if k != "words"} for item in LENGTHS],
        "narrators": [{k: v for k, v in item.items() if k not in ("voices", "style", "speed")} for item in NARRATORS],
    }
