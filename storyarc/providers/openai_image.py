"""OpenAI image adapter (gpt-image-2) for page illustrations."""
import base64
import logging
from typing import Any, Dict, List, Tuple

import config
from providers import _http
from providers.base import ImageProvider, ProviderError

logger = logging.getLogger(__name__)

IMAGES_URL = "https://api.openai.com/v1/images/generations"
EDITS_URL = "https://api.openai.com/v1/images/edits"  # same models; takes reference pictures


class OpenAIImage(ImageProvider):
    name = "openai"

    def __init__(self) -> None:
        self.model = config.OPENAI_IMAGE_MODEL
        self.quality = config.OPENAI_IMAGE_QUALITY
        self._key = _http.require_key(config.OPENAI_API_KEY, "OPENAI_API_KEY", "OpenAI")

    async def generate(
        self, prompt: str, *, portrait: bool = True, references: List[Tuple[bytes, str]] = ()
    ) -> Tuple[bytes, str]:
        fields: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1536" if portrait else "1536x1024",
            "quality": self.quality,
            "output_format": "webp",
            "output_compression": 80,
        }
        if references:
            # The edits endpoint paints a new picture that takes after the attached ones.
            headers = {"Authorization": f"Bearer {self._key}"}
            files = [
                ("image[]", (f"ref{i + 1}.{mime.split('/')[-1]}", data, mime))
                for i, (data, mime) in enumerate(references)
            ]
            async with _http.client(headers, timeout=240) as http:
                resp = await http.post(EDITS_URL, data={k: str(v) for k, v in fields.items()}, files=files)
        else:
            headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}
            async with _http.client(headers, timeout=180) as http:
                resp = await http.post(IMAGES_URL, json=fields)
        _http.raise_for_status(resp, "OpenAI images")
        data = resp.json()
        items = data.get("data") or []
        encoded = items[0].get("b64_json") if items else None
        if not encoded:
            raise ProviderError("OpenAI returned no picture. Please try again.")
        usage = data.get("usage") or {}
        logger.info(
            "OpenAI %s (%s): %s output tokens, %s input tokens, %d reference(s)",
            self.model, self.quality, usage.get("output_tokens"), usage.get("input_tokens"), len(references),
        )
        return base64.b64decode(encoded), "webp"
