"""OpenAI transcription adapter (speech to text)."""
from typing import Optional

import config
from providers import _http
from providers.base import STTProvider, Transcript

TRANSCRIPTIONS_URL = "https://api.openai.com/v1/audio/transcriptions"


class OpenAISTT(STTProvider):
    name = "openai"

    def __init__(self) -> None:
        self.model = config.OPENAI_STT_MODEL
        self._key = _http.require_key(config.OPENAI_API_KEY, "OPENAI_API_KEY", "OpenAI")

    async def transcribe(
        self,
        audio: bytes,
        filename: str,
        content_type: str,
        language: Optional[str] = None,
    ) -> Transcript:
        fields = {"model": self.model}
        if language:
            # gpt-transcribe takes a `languages[]` list; older models take a single `language`.
            if self.model.startswith("gpt-transcribe"):
                fields["languages[]"] = language
            else:
                fields["language"] = language
        headers = {"Authorization": f"Bearer {self._key}"}
        async with _http.client(headers) as http:
            resp = await http.post(
                TRANSCRIPTIONS_URL,
                data=fields,
                files={"file": (filename, audio, content_type or "application/octet-stream")},
            )
        _http.raise_for_status(resp, "OpenAI transcription")
        data = resp.json()
        detected = None
        langs = data.get("languages") or []
        if langs and isinstance(langs[0], dict):
            detected = langs[0].get("code")
        return Transcript(text=(data.get("text") or "").strip(), language=detected or data.get("language"))
