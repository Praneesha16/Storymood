"""Shared HTTP helpers for adapters: one client factory and one error translator."""
import logging
from typing import Dict

import httpx

import config
from providers.base import ProviderError

logger = logging.getLogger(__name__)


def client(headers: Dict[str, str], timeout: float = config.HTTP_TIMEOUT_SECONDS) -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=headers, timeout=timeout, trust_env=False)


def require_key(value: str, env_name: str, vendor: str) -> str:
    if not value:
        raise ProviderError(f"{vendor} is selected but {env_name} is empty. Add it to storyarc/.env.")
    return value


def raise_for_status(resp: httpx.Response, vendor: str) -> None:
    """Turn a non-2xx response into a ProviderError with the vendor's own message."""
    if resp.is_success:
        return
    detail = ""
    try:
        body = resp.json()
        detail = (body.get("error") or {}).get("message") if isinstance(body.get("error"), dict) else body.get("error")
        detail = detail or body.get("message") or body.get("detail") or ""
    except ValueError:
        detail = resp.text[:300]
    logger.error("%s HTTP %s: %s", vendor, resp.status_code, detail)
    if resp.status_code in (401, 403):
        raise ProviderError(f"{vendor} rejected the API key. Check storyarc/.env.")
    if resp.status_code == 429:
        raise ProviderError(f"{vendor} rate limit reached. Please try again in a moment.")
    raise ProviderError(f"{vendor} error {resp.status_code}: {detail or 'no details'}")
