"""Library records as JSON files on disk (one per story, one per user). The default for a laptop.

Folder: backend/data/{stories,users}. Switch to DynamoDB with STORE_PROVIDER=dynamodb.
"""
import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import config
from providers.base import StoreProvider


class LocalStore(StoreProvider):
    name = "local"

    def __init__(self) -> None:
        self.root = config.DATA_DIR
        for sub in ("stories", "users"):
            os.makedirs(os.path.join(self.root, sub), exist_ok=True)
        self._lock = asyncio.Lock()

    def _path(self, kind: str, key: str) -> str:
        safe = "".join(c if (c.isalnum() or c in "-_.") else "_" for c in key)  # ids like guest:a@b stay unique and file-safe
        return os.path.join(self.root, kind, f"{safe}.json")

    def _read(self, kind: str, key: str) -> Optional[Dict[str, Any]]:
        path = self._path(kind, key)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, kind: str, key: str, record: Dict[str, Any]) -> None:
        path = self._path(kind, key)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False)
        os.replace(tmp, path)

    def _all(self, kind: str) -> List[Dict[str, Any]]:
        folder = os.path.join(self.root, kind)
        out = []
        for name in os.listdir(folder):
            if name.endswith(".json"):
                with open(os.path.join(folder, name), encoding="utf-8") as fh:
                    out.append(json.load(fh))
        return out

    async def put_story(self, record: Dict[str, Any]) -> None:
        async with self._lock:
            self._write("stories", record["id"], record)

    async def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        return self._read("stories", story_id)

    async def update_story(self, story_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        async with self._lock:
            record = self._read("stories", story_id)
            if not record:
                return None
            record.update(fields)
            self._write("stories", story_id, record)
            return record

    async def delete_story(self, story_id: str) -> None:
        async with self._lock:
            path = self._path("stories", story_id)
            if os.path.isfile(path):
                os.remove(path)

    async def stories_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        items = [r for r in self._all("stories") if r.get("owner_id") == owner_id]
        return sorted(items, key=lambda r: r.get("created_at", ""), reverse=True)

    async def stories_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        items = [r for r in self._all("stories") if r.get("status") == status]
        items.sort(key=lambda r: r.get("published_at") or r.get("created_at", ""), reverse=True)
        return items[:limit]

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._read("users", user_id)

    async def put_user(self, record: Dict[str, Any]) -> None:
        async with self._lock:
            self._write("users", record["id"], record)
