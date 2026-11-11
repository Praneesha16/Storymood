"""Turns a recorded idea into text with the configured STT adapter."""
import logging
from typing import Optional

import config
from models.story_model import TranscriptionResponse
from providers import registry
from providers.base import ProviderError

logger = logging.getLogger(__name__)

SUPPORTED_CODES = {"en", "hi", "te", "ta", "ml"}


async def transcribe(audio: bytes, filename: str, content_type: str, language: Optional[str]) -> TranscriptionResponse:
    if not audio:
        raise ProviderError("The recording was empty. Hold the microphone button and try again.")
    if len(audio) > config.MAX_UPLOAD_BYTES:
        raise ProviderError("That recording is too long. Please keep it under a minute or two.")

    stt = registry.stt()
    hint = language if language in SUPPORTED_CODES else None
    logger.info("Transcribing %d bytes via %s/%s hint=%s", len(audio), stt.name, stt.model, hint)
    result = await stt.transcribe(audio, filename, content_type, hint)

    detected = (result.language or "").lower()[:2] or None
    if detected not in SUPPORTED_CODES:
        detected = None
    return TranscriptionResponse(text=result.text, language=detected, provider=stt.name)
