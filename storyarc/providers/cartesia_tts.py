"""Cartesia Sonic adapter (text to speech). Default narrator engine."""
from typing import Any, Dict

import config
from providers import _http
from providers.base import ProviderError, TTSProvider, VoiceSpec

TTS_BYTES_URL = "https://api.cartesia.ai/tts/bytes"
CLONE_URL = "https://api.cartesia.ai/voices/clone"


class CartesiaTTS(TTSProvider):
    name = "cartesia"
    audio_format = "mp3"
    max_chars = 2000
    supports_cloning = True

    def __init__(self) -> None:
        self.model = config.CARTESIA_TTS_MODEL
        self._key = _http.require_key(config.CARTESIA_API_KEY, "CARTESIA_API_KEY", "Cartesia")

    async def synthesize(self, text: str, voice: VoiceSpec, language: str) -> bytes:
        body: Dict[str, Any] = {
            "model_id": self.model,
            "transcript": text,
            "voice": {"mode": "id", "id": voice.voice},
            "language": language,
            "output_format": {"container": "mp3", "sample_rate": 44100, "bit_rate": 128000},
        }
        if self.model.startswith("sonic-3"):
            # generation_config exists on sonic-3 and newer. Speed range is 0.6 to 1.5.
            body["generation_config"] = {"speed": max(0.6, min(1.5, voice.speed))}
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Cartesia-Version": config.CARTESIA_API_VERSION,
            "Content-Type": "application/json",
        }
        async with _http.client(headers) as http:
            resp = await http.post(TTS_BYTES_URL, json=body)
        _http.raise_for_status(resp, "Cartesia")
        return resp.content

    async def clone_voice(self, audio: bytes, filename: str, content_type: str, name: str, language: str) -> str:
        """Clone a voice from a 5 to 20 second clip. The voice stays private to this Cartesia account."""
        headers = {"Authorization": f"Bearer {self._key}", "Cartesia-Version": config.CARTESIA_API_VERSION}
        fields = {"name": name[:60], "language": language, "tagline": "StoryMood family voice"}
        async with _http.client(headers) as http:
            resp = await http.post(
                CLONE_URL,
                data=fields,
                files={"clip": (filename, audio, content_type or "application/octet-stream")},
            )
        _http.raise_for_status(resp, "Cartesia voice clone")
        voice_id = resp.json().get("id")
        if not voice_id:
            raise ProviderError("Cartesia did not return a voice id for the clone.")
        return voice_id
