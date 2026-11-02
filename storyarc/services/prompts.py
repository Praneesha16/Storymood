"""Prompt building for children's stories. Edit here to change the writing style."""
from typing import Any, Dict

import catalog
from models.story_model import StoryRequest

SYSTEM_PROMPT = """You are StoryMood, a beloved children's storyteller.

Rules you always follow:
- Write for children. Keep everything kind, safe and age-appropriate: no graphic violence, no horror,
  no romance, no weapons used against people, no cruelty, no scary endings.
- Every story has a clear beginning, a middle with one small problem, and a happy, satisfying ending.
- Use vivid senses, playful sounds, a little humour and warmth. Show feelings through actions.
- Write in the requested language only, using natural phrasing a native-speaking child would hear at home.
  Never transliterate; use the language's own script.
- Output plain prose paragraphs separated by blank lines. No headings, no bullet points, no markdown,
  no stage directions, no notes to the reader.
- The text will be read aloud by a voice engine, so avoid symbols, emoji and abbreviations."""

STORY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "A short, fun title of at most 8 words in the story's language."},
        "story": {"type": "string", "description": "The complete story as plain paragraphs separated by blank lines."},
    },
    "required": ["title", "story"],
    "additionalProperties": False,
}


def build_story_prompt(req: StoryRequest) -> str:
    theme = catalog.theme(req.theme)
    feeling = catalog.feeling(req.feeling)
    age = catalog.age_group(req.age_group)
    length = catalog.length(req.length)
    lang = catalog.language(req.language)

    lines = [
        f"Write a {feeling['label'].lower()} {theme['label'].lower()} story in {lang['label']} for a child aged {age['label']}.",
        f"Theme ideas: {theme['hint']}.",
        f"Feeling: {feeling['hint']}.",
        f"Age guidance: {age['guidance']}.",
        f"Length: about {length['words']} words.",
    ]
    if req.characters:
        people = ", ".join(
            f"{c.name} ({c.trait})" if c.trait.strip() else c.name for c in req.characters
        )
        lines.append(f"Main characters, use these names exactly: {people}.")
    if req.idea.strip():
        lines.append(f"The child asked for this: \"{req.idea.strip()}\". Weave it in as the heart of the story.")
    lines.append("Return JSON with a title and the full story.")
    return "\n".join(lines)
