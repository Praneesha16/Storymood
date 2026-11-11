"""Narration and pictures kept under storyarc/static and served by this server. Laptop default."""
import asyncio
import os

import config
from providers.base import FileStore


class LocalFiles(FileStore):
    name = "local"

    async def save(self, kind: str, filename: str, data: bytes, content_type: str) -> str:
        folder = os.path.join(config.STATIC_DIR, kind)
        os.makedirs(folder, exist_ok=True)

        def write() -> None:
            with open(os.path.join(folder, filename), "wb") as fh:
                fh.write(data)

        await asyncio.to_thread(write)
        return f"/static/{kind}/{filename}"
