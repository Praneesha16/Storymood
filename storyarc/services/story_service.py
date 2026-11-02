"""Turns a StoryRequest into a finished story using the configured LLM adapter."""
import json
import logging
import re

import catalog
from models.story_model import StoryMeta, StoryRequest, StoryResponse
from providers import registry
from providers.base import ProviderError
from services.prompts import STORY_SCHEMA, SYSTEM_PROMPT, build_story_prompt

logger = logging.getLogger(__name__)

READ_ALOUD_WORDS_PER_MINUTE = 130


def _parse(text: str) -> tuple:
    """Return (title, story). Tolerates models that wrap JSON in fences or skip it."""
    cleaned = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text.strip())
    try:
        data = json.loads(cleaned)
        title = str(data.get("title", "")).strip()
        story = str(data.get("story", "")).strip()
        if story:
            return title or "My Story", story
    except (ValueError, AttributeError):
        pass
    paragraphs = [p.strip() for p in cleaned.split("\n") if p.strip()]
    if not paragraphs:
        raise ProviderError("The story came back empty. Please try again.")
    if len(paragraphs) > 1 and len(paragraphs[0]) <= 80:
        return paragraphs[0].strip("#* "), "\n\n".join(paragraphs[1:])
    return "My Story", "\n\n".join(paragraphs)


async def generate(req: StoryRequest) -> StoryResponse:
    llm = registry.llm()
    prompt = build_story_prompt(req)
    target_words = catalog.length(req.length)["words"]
    # Non-Latin scripts tokenize heavily; give generous headroom for the longest stories.
    max_tokens = min(16000, 1500 + target_words * 8)

    logger.info("Story via %s/%s: theme=%s feeling=%s lang=%s", llm.name, llm.model, req.theme, req.feeling, req.language)
    raw = await llm.generate(SYSTEM_PROMPT, prompt, max_tokens=max_tokens, json_schema=STORY_SCHEMA)
    title, story = _parse(raw)

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
    return StoryResponse(title=title, story_text=story, meta=meta)
