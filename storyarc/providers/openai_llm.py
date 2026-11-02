"""OpenAI Responses API adapter for story writing."""
import logging
from typing import Any, Dict, Optional

import config
from providers import _http
from providers.base import LLMProvider, ProviderError

logger = logging.getLogger(__name__)

RESPONSES_URL = "https://api.openai.com/v1/responses"


class OpenAILLM(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        self.model = config.OPENAI_LLM_MODEL
        self._key = _http.require_key(config.OPENAI_API_KEY, "OPENAI_API_KEY", "OpenAI")

    async def generate(
        self,
        system: str,
        prompt: str,
        *,
        max_tokens: int = 4000,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        body: Dict[str, Any] = {
            "model": self.model,
            "instructions": system,
            "input": prompt,
            "max_output_tokens": max_tokens,
        }
        if config.OPENAI_REASONING_EFFORT:
            body["reasoning"] = {"effort": config.OPENAI_REASONING_EFFORT}
        if json_schema:
            body["text"] = {
                "format": {"type": "json_schema", "name": "story", "schema": json_schema, "strict": True}
            }

        headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}
        async with _http.client(headers) as http:
            resp = await http.post(RESPONSES_URL, json=body)
        _http.raise_for_status(resp, "OpenAI")
        data = resp.json()

        if data.get("status") == "incomplete":
            reason = (data.get("incomplete_details") or {}).get("reason", "unknown")
            raise ProviderError(f"OpenAI stopped early ({reason}). Try a shorter story length.")

        text = "".join(
            part.get("text", "")
            for item in data.get("output", [])
            if item.get("type") == "message"
            for part in item.get("content", [])
            if part.get("type") == "output_text"
        )
        if not text.strip():
            raise ProviderError("OpenAI returned an empty story. Please try again.")
        usage = data.get("usage", {})
        logger.info("OpenAI %s: %s in / %s out tokens", self.model, usage.get("input_tokens"), usage.get("output_tokens"))
        return text
