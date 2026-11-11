"""Paints one picture for a story page or cover with the configured image adapter."""
import asyncio
import base64
import logging
import os
import uuid
from typing import List, Tuple

import config
from models.story_model import IllustrateRequest, IllustrateResponse
from providers import registry
from providers.base import ProviderError

MAX_REFERENCE_BYTES = 1_000_000

logger = logging.getLogger(__name__)

# The same style line on every picture keeps a story's pages looking like one book.
STYLE = (
    "Children's storybook illustration in soft watercolour and coloured pencil, warm parchment tones, "
    "gentle light, friendly rounded characters, cosy and safe. Absolutely no text, letters, words, "
    "captions or signatures anywhere in the picture."
)

_slots = asyncio.Semaphore(4)  # pages are painted in parallel; stay polite to the vendor


def build_prompt(req: IllustrateRequest) -> str:
    parts = [STYLE]
    if req.references:
        who = "; ".join(f"picture {i + 1} shows {r.name}" for i, r in enumerate(req.references))
        parts.append(
            f"Reference pictures are attached: {who}. Paint these characters so they clearly take after their "
            "reference pictures (same face, hair, skin, colours and clothes), redrawn in the storybook style above."
        )
    if req.characters.strip():
        parts.append(f"The characters always look like this: {req.characters.strip()}")
    if req.kind == "cover":
        parts.append(f"A book cover picture for a story called \"{req.title}\" (do not write the title): {req.scene.strip()}")
    else:
        parts.append(f"Scene: {req.scene.strip()}")
    return "\n".join(parts)


def _decode(references) -> List[Tuple[bytes, str]]:
    """Data URLs from the browser -> (bytes, mime). Kept in memory for this request only."""
    out: List[Tuple[bytes, str]] = []
    for ref in references:
        header, _, payload = ref.image.partition(",")
        mime = header[5:].split(";")[0]
        try:
            raw = base64.b64decode(payload, validate=True)
        except (ValueError, base64.binascii.Error):
            raise ProviderError(f"The picture for {ref.name} could not be read.")
        if len(raw) > MAX_REFERENCE_BYTES:
            raise ProviderError(f"The picture for {ref.name} is too large.")
        out.append((raw, mime))
    return out


async def illustrate(req: IllustrateRequest) -> IllustrateResponse:
    image = registry.image()
    prompt = build_prompt(req)
    references = _decode(req.references)
    async with _slots:
        data, ext = await image.generate(prompt, portrait=True, references=references)
    url = await registry.files().save("images", f"{uuid.uuid4()}.{ext}", data, f"image/{ext}")
    logger.info("Painted %s picture via %s/%s (%d KB)", req.kind, image.name, image.model, len(data) // 1024)
    return IllustrateResponse(image_url=url, provider=image.name, model=image.model)
