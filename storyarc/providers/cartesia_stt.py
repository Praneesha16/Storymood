"""Cartesia Ink adapter (speech to text). Secondary option; OpenAI is the default."""
from typing import Optional

import config
from providers import _http
from providers.base import STTProvider, Transcript

STT_URL = "https://api.cartesia.ai/stt"


class CartesiaSTT(STTProvider):
    name = "cartesia"

    def __init__(self) -> None:
        self.model = config.CARTESIA_STT_MODEL
        self._key = _http.require_key(config.CARTESIA_API_KEY, "CARTESIA_API_KEY", "Cartesia")

    async def transcribe(
        self,
        audio: bytes,
        filename: str,
        content_type: str,
        language: Optional[str] = None,
    ) -> Transcript:
        # Ink does not auto-detect; it defaults to English when no language is given.
        fields = {"model": self.model, "language": language or "en"}
        headers = {"Authorization": f"Bearer {self._key}", "Cartesia-Version": config.CARTESIA_API_VERSION}
        async with _http.client(headers) as http:
            resp = await http.post(
                STT_URL,
                data=fields,
                files={"file": (filename, audio, content_type or "application/octet-stream")},
            )
        _http.raise_for_status(resp, "Cartesia transcription")
        data = resp.json()
        return Transcript(text=(data.get("text") or "").strip(), language=data.get("language"))
