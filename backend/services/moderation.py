"""Guardrail on everything a family types or uploads, before it reaches the writer or the painter.

Uses OpenAI's Moderation API (free): text and images are scored for sexual, hateful, violent,
harassing and self-harm content. Anything flagged is refused with a gentle message and never
sent further. MODERATION=none switches it off (local testing only).
"""
import logging
from typing import Iterable, List, Optional

import config
from providers import _http

logger = logging.getLogger(__name__)

MODERATIONS_URL = "https://api.openai.com/v1/moderations"
FRIENDLY = "That does not belong in a children's story. Let's try a different idea."


class ContentRefused(Exception):
    """Input that failed moderation. Shown to the user as-is."""


async def check(texts: Iterable[str] = (), images: Iterable[str] = ()) -> None:
    """Raise ContentRefused if any text or image (data URL or http URL) is flagged."""
    if config.MODERATION == "none":
        return
    inputs: List[dict] = [{"type": "text", "text": t[:4000]} for t in texts if t and t.strip()]
    inputs += [{"type": "image_url", "image_url": {"url": u}} for u in images if u]
    if not inputs:
        return
    headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}", "Content-Type": "application/json"}
    async with _http.client(headers, timeout=60) as http:
        resp = await http.post(MODERATIONS_URL, json={"model": config.OPENAI_MODERATION_MODEL, "input": inputs})
    _http.raise_for_status(resp, "OpenAI moderation")
    results = resp.json().get("results", [])
    for result in results:
        if result.get("flagged"):
            cats = [k for k, v in (result.get("categories") or {}).items() if v]
            logger.warning("Moderation refused input: %s", ", ".join(cats))
            raise ContentRefused(FRIENDLY)


def story_inputs(idea: str, names: Iterable[str], traits: Iterable[str]) -> List[str]:
    return [idea, *names, *traits]
