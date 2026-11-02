"""Reads a story aloud with the configured TTS adapter and serves the file from /static/audio."""
import asyncio
import logging
import os
import re
import uuid
from typing import List

import catalog
import config
from models.story_model import NarrationRequest, NarrationResponse, VoiceCloneResponse
from providers import registry
from providers.base import ProviderError, VoiceSpec

logger = logging.getLogger(__name__)

PARALLEL_CHUNKS = 3


def _sentences(paragraph: str, max_chars: int) -> List[str]:
    """Split one over-long paragraph on sentence ends."""
    out: List[str] = []
    current = ""
    for sentence in re.split(r"(?<=[.!?।])\s+", paragraph):
        if current and len(current) + len(sentence) + 1 > max_chars:
            out.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        out.append(current)
    return out


def _chunks(text: str, max_chars: int) -> List[str]:
    """Pack paragraphs into the fewest requests that stay under the vendor's limit.

    Paragraph breaks are kept inside a chunk so the voice still pauses between them.
    """
    text = re.sub(r"[ \t]+", " ", text).strip()
    units: List[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if paragraph:
            units.extend([paragraph] if len(paragraph) <= max_chars else _sentences(paragraph, max_chars))

    pieces: List[str] = []
    current = ""
    for unit in units:
        if current and len(current) + len(unit) + 2 > max_chars:
            pieces.append(current)
            current = unit
        else:
            current = f"{current}\n\n{unit}" if current else unit
    if current:
        pieces.append(current)
    return pieces


async def narrate(req: NarrationRequest) -> NarrationResponse:
    tts = registry.tts()
    if req.voice_id:
        # A custom (cloned) voice: plain, slightly slow storytelling pace.
        voice_id = req.voice_id
        spec = VoiceSpec(voice=voice_id, speed=0.95, style="A warm family member reading a story to a child.")
    else:
        entry = catalog.narrator(req.narrator)
        voice_id = catalog.resolve_voice(req.narrator, tts.name, req.language)
        if not voice_id:
            raise ProviderError(
                f"Narrator '{req.narrator}' has no voice for provider '{tts.name}'. Add one under 'voices' in catalog.py."
            )
        spec = VoiceSpec(voice=voice_id, speed=entry.get("speed", 1.0), style=entry.get("style", ""))

    parts = _chunks(req.text, tts.max_chars)
    logger.info("Narrating %d chunk(s) via %s/%s voice=%s lang=%s", len(parts), tts.name, tts.model, voice_id, req.language)

    semaphore = asyncio.Semaphore(PARALLEL_CHUNKS)

    async def synth(part: str) -> bytes:
        async with semaphore:
            return await tts.synthesize(part, spec, req.language)

    audio_parts = await asyncio.gather(*(synth(p) for p in parts))

    os.makedirs(config.AUDIO_FILES_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.{tts.audio_format}"
    with open(os.path.join(config.AUDIO_FILES_DIR, filename), "wb") as fh:
        for blob in audio_parts:
            fh.write(blob)

    return NarrationResponse(audio_url=f"{config.AUDIO_FILES_URL_PATH}/{filename}", provider=tts.name, voice=voice_id)


MIN_CLIP_BYTES = 20_000  # roughly 3 seconds of compressed audio


async def clone(audio: bytes, filename: str, content_type: str, name: str, language: str) -> VoiceCloneResponse:
    tts = registry.tts()
    if not tts.supports_cloning:
        raise ProviderError(f"The '{tts.name}' voice provider cannot clone voices. Switch TTS_PROVIDER to one that can.")
    if len(audio) < MIN_CLIP_BYTES:
        raise ProviderError("That recording is too short. Read the whole sentence, about ten seconds.")
    if len(audio) > config.MAX_UPLOAD_BYTES:
        raise ProviderError("That recording is too long. Keep it under a minute.")
    clean_name = (name or "My voice").strip()[:60] or "My voice"
    logger.info("Cloning voice '%s' via %s (%d bytes, lang=%s)", clean_name, tts.name, len(audio), language)
    voice_id = await tts.clone_voice(audio, filename, content_type, clean_name, language)
    return VoiceCloneResponse(voice_id=voice_id, name=clean_name, provider=tts.name)
