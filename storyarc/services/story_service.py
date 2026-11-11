"""Turns a StoryRequest into a finished story using the configured LLM adapter."""
import json
import logging
import re
from typing import Any, List, Tuple

import catalog
import config
from models.story_model import Paragraph, StoryArt, StoryMeta, StoryPage, StoryRequest, StoryResponse
from providers import registry
from providers.base import ProviderError
from services.prompts import STORY_SCHEMA, SYSTEM_PROMPT, build_story_prompt

logger = logging.getLogger(__name__)

READ_ALOUD_WORDS_PER_MINUTE = 130


def _clean_mood(value: Any, fallback: str) -> str:
    value = str(value or "").strip().lower()
    return value if catalog.mood(value) else fallback


def _parse(text: str, fallback_mood: str) -> Tuple[str, str, List[Paragraph], StoryArt]:
    """Return (title, mood, paragraphs, art). Tolerates models that wrap JSON in fences or skip it."""
    cleaned = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text.strip())
    try:
        data = json.loads(cleaned)
        title = str(data.get("title", "")).strip() or "My Story"
        mood = _clean_mood(data.get("mood"), fallback_mood)
        art_raw = data.get("art") if isinstance(data.get("art"), dict) else {}
        art = StoryArt(characters=str(art_raw.get("characters", "")).strip(), cover=str(art_raw.get("cover", "")).strip())
        items = data.get("paragraphs")
        if isinstance(items, list):
            paragraphs = [
                Paragraph(
                    text=str(p.get("text", "")).strip(),
                    mood=_clean_mood(p.get("mood"), mood),
                    scene=str(p.get("scene", "")).strip(),
                )
                for p in items
                if isinstance(p, dict) and str(p.get("text", "")).strip()
            ]
            if paragraphs:
                return title, mood, paragraphs, art
        story = str(data.get("story", "")).strip()  # older shape: one block of text
        if story:
            return title, mood, [Paragraph(text=p.strip(), mood=mood) for p in re.split(r"\n\s*\n", story) if p.strip()], art
    except (ValueError, AttributeError):
        pass
    lines = [p.strip() for p in cleaned.split("\n") if p.strip()]
    if not lines:
        raise ProviderError("The story came back empty. Please try again.")
    title = "My Story"
    if len(lines) > 1 and len(lines[0]) <= 80:
        title, lines = lines[0].strip("#* "), lines[1:]
    return title, fallback_mood, [Paragraph(text=p, mood=fallback_mood) for p in lines], StoryArt()


def paginate(paragraphs: List[Paragraph]) -> List[StoryPage]:
    """Group paragraphs into book pages; each page's picture shows what its paragraphs describe."""
    pages: List[StoryPage] = []
    current: List[int] = []
    size = 0
    for i, p in enumerate(paragraphs):
        if current and size + len(p.text) > config.CHARS_PER_PAGE:
            pages.append(StoryPage(paragraphs=current, scene=" ".join(paragraphs[j].scene for j in current if paragraphs[j].scene)))
            current, size = [], 0
        current.append(i)
        size += len(p.text)
    if current:
        pages.append(StoryPage(paragraphs=current, scene=" ".join(paragraphs[j].scene for j in current if paragraphs[j].scene)))
    return pages


async def generate(req: StoryRequest) -> StoryResponse:
    llm = registry.llm()
    prompt = build_story_prompt(req)
    target_words = catalog.length(req.length)["words"]
    # Non-Latin scripts tokenize heavily; give generous headroom for the longest stories.
    max_tokens = min(16000, 1500 + target_words * 8)

    logger.info("Story via %s/%s: theme=%s feeling=%s lang=%s", llm.name, llm.model, req.theme, req.feeling, req.language)
    raw = await llm.generate(SYSTEM_PROMPT, prompt, max_tokens=max_tokens, json_schema=STORY_SCHEMA)
    title, mood, paragraphs, art = _parse(raw, catalog.default_mood(req.feeling))
    story = "\n\n".join(p.text for p in paragraphs)
    pages = paginate(paragraphs)

    # Background music is chosen once, here, so a saved story always replays with the same track.
    music_url = await registry.music().pick(mood, catalog.mood(mood).get("like", []))

    word_count = len(story.split())
    meta = StoryMeta(
        theme=req.theme,
        feeling=req.feeling,
        age_group=req.age_group,
        length=req.length,
        language=req.language,
        narrator=req.narrator,
        characters=[c.name for c in req.characters],
        word_count=word_count,
        estimated_minutes=max(1, round(word_count / READ_ALOUD_WORDS_PER_MINUTE)),
        provider=llm.name,
        model=llm.model,
    )
    return StoryResponse(
        title=title, story_text=story, meta=meta, mood=mood, music_url=music_url,
        paragraphs=paragraphs, pages=pages, art=art,
    )
