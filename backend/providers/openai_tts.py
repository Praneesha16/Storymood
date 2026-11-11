"""OpenAI speech adapter (text to speech). Secondary option; Cartesia is the default."""
import config
from providers import _http
from providers.base import TTSProvider, VoiceSpec

SPEECH_URL = "https://api.openai.com/v1/audio/speech"


class OpenAITTS(TTSProvider):
    name = "openai"
    audio_format = "mp3"
    max_chars = 3500  # the endpoint accepts up to 4096 characters per request

    def __init__(self) -> None:
        self.model = config.OPENAI_TTS_MODEL
        self._key = _http.require_key(config.OPENAI_API_KEY, "OPENAI_API_KEY", "OpenAI")

    async def synthesize(self, text: str, voice: VoiceSpec, language: str) -> bytes:
        body = {
            "model": self.model,
            "voice": voice.voice,
            "input": text,
            "response_format": self.audio_format,
            "speed": max(0.25, min(4.0, voice.speed)),
        }
        if (voice.style or voice.emotion) and self.model.startswith("gpt-"):
            # `instructions` is only honoured by the gpt-* speech models, not tts-1.
            mood = f" Read this passage in a {voice.emotion} tone." if voice.emotion else ""
            body["instructions"] = f"{voice.style}{mood}".strip()
        headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}
        async with _http.client(headers) as http:
            resp = await http.post(SPEECH_URL, json=body)
        _http.raise_for_status(resp, "OpenAI speech")
        return resp.content
