"""Per-user limits on the routes that cost money. In-memory, per process: enough for one server;
move the counters to DynamoDB when there is more than one."""
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, status

import config

_events: Dict[str, Deque[float]] = defaultdict(deque)


def hit(user_id: str, action: str, limit: int, per_seconds: int = 3600) -> None:
    """Record one `action` by `user_id`; refuse with 429 when over `limit` in the window."""
    if not config.RATE_LIMITS:
        return
    key = f"{user_id}:{action}"
    now = time.time()
    window = _events[key]
    while window and now - window[0] > per_seconds:
        window.popleft()
    if len(window) >= limit:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "That is a lot of stories for one hour. Please come back a little later.",
        )
    window.append(now)
