"""No illustrations. Select with IMAGE_PROVIDER=none."""
from typing import List, Tuple

from providers.base import ImageProvider, ProviderError


class DisabledImage(ImageProvider):
    name = "none"
    enabled = False

    async def generate(self, prompt: str, *, portrait: bool = True, references: List[Tuple[bytes, str]] = ()) -> Tuple[bytes, str]:
        raise ProviderError("Pictures are switched off. Set IMAGE_PROVIDER in backend/.env to enable them.")
