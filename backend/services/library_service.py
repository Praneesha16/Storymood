"""Every family's stories on the server, the free-story allowance, and the community shelf.

A story record is created when a story is written, then narration and pictures attach to it.
Statuses: private -> pending (grown-up asked to share, with consent) -> published | rejected.
Reports from listeners hide a story again (pending) once there are several.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

import config
from models.story_model import StoryResponse
from providers import registry
from services import moderation
from services.auth import User

logger = logging.getLogger(__name__)

REPORTS_TO_HIDE = 3
PUBLIC_FIELDS = ("id", "title", "meta", "mood", "pictures", "published_at", "owner_name", "language", "has_audio")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_admin(user: User) -> bool:
    if config.AUTH_MODE == "none":
        return True  # on a laptop the developer reviews
    return bool(user.email) and user.email.lower() in {e.lower() for e in config.ADMIN_EMAILS}


# ---- allowance ---------------------------------------------------------------------------
async def _user_record(user: User) -> Dict[str, Any]:
    store = registry.store()
    rec = await store.get_user(user.id)
    if not rec:
        rec = {"id": user.id, "email": user.email, "name": user.name, "free_used": 0, "credits": 0, "created_at": _now()}
        await store.put_user(rec)
    return rec


async def allowance(user: User) -> Dict[str, Any]:
    rec = await _user_record(user)
    return {
        "free_total": config.FREE_STORIES,
        "free_left": max(0, config.FREE_STORIES - int(rec.get("free_used", 0))),
        "credits": int(rec.get("credits", 0)),
        "unlimited": user.guest,
        "admin": is_admin(user),
    }


async def spend_story(user: User) -> None:
    """Take one story from the free allowance, then from credits; refuse when both are empty."""
    if user.guest:
        return
    store = registry.store()
    rec = await _user_record(user)
    if int(rec.get("free_used", 0)) < config.FREE_STORIES:
        rec["free_used"] = int(rec.get("free_used", 0)) + 1
    elif int(rec.get("credits", 0)) > 0:
        rec["credits"] = int(rec["credits"]) - 1
    else:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            f"Your {config.FREE_STORIES} free stories are used up. Story packs are coming soon; the community shelf is always free.",
        )
    await store.put_user(rec)


async def grant_credits(user_id: str, credits: int) -> Dict[str, Any]:
    store = registry.store()
    rec = await store.get_user(user_id) or {"id": user_id, "free_used": 0, "credits": 0, "created_at": _now()}
    rec["credits"] = max(0, int(rec.get("credits", 0)) + credits)
    await store.put_user(rec)
    return rec


# ---- records -----------------------------------------------------------------------------
async def create(user: User, story: StoryResponse, voice_name: str = "", has_personal_pictures: bool = False) -> Dict[str, Any]:
    record = {
        "id": str(uuid.uuid4()),
        "owner_id": user.id,
        "owner_name": (user.name or user.email.split("@")[0]).split(" ")[0] or "a family",
        "created_at": _now(),
        "status": "private",
        "title": story.title,
        "story_text": story.story_text,
        "paragraphs": [p.dict() for p in story.paragraphs],
        "pages": [p.dict() for p in story.pages],
        "mood": story.mood,
        "music_url": story.music_url,
        "art": story.art.dict() if story.art else None,
        "meta": story.meta.dict(),
        "language": story.meta.language,
        "voice_name": voice_name,
        "audio_url": None,
        "cues": [],
        "pictures": {},
        "has_audio": False,
        "has_personal_pictures": has_personal_pictures,
        "consent": False,
        "published_at": None,
        "review_note": "",
        "reports": [],
    }
    await registry.store().put_story(record)
    return record


async def _owned(story_id: str, user: User, reviewer_ok: bool = False) -> Dict[str, Any]:
    """The record, if `user` owns it (or, when reviewer_ok, is a reviewer)."""
    record = await registry.store().get_story(story_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That story is not here any more.")
    if record["owner_id"] != user.id and not (reviewer_ok and is_admin(user)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "That story belongs to another family.")
    return record


async def attach_audio(story_id: str, user: User, audio_url: str, cues: List[Dict[str, Any]]) -> None:
    record = await registry.store().get_story(story_id)
    if record and record["owner_id"] == user.id:
        await registry.store().update_story(story_id, audio_url=audio_url, cues=cues, has_audio=True)


async def attach_picture(story_id: str, user: User, key: str, url: str, personal: bool) -> None:
    record = await registry.store().get_story(story_id)
    if record and record["owner_id"] == user.id:
        pictures = dict(record.get("pictures") or {})
        pictures[key] = url
        await registry.store().update_story(
            story_id, pictures=pictures, has_personal_pictures=record.get("has_personal_pictures") or personal
        )


async def mine(user: User) -> List[Dict[str, Any]]:
    return await registry.store().stories_by_owner(user.id)


async def get(story_id: str, user: Optional[User]) -> Dict[str, Any]:
    record = await registry.store().get_story(story_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That story is not here any more.")
    if record["status"] == "published" or (user and (record["owner_id"] == user.id or is_admin(user))):
        return record
    raise HTTPException(status.HTTP_403_FORBIDDEN, "That story is private.")


async def delete(story_id: str, user: User) -> None:
    await _owned(story_id, user)
    await registry.store().delete_story(story_id)


# ---- publishing ----------------------------------------------------------------------------
async def publish(story_id: str, user: User, consent: bool) -> Dict[str, Any]:
    record = await _owned(story_id, user)
    if not consent:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Please confirm you are happy to share this story.")
    # Belt and braces: the finished text is checked again before it can reach other families.
    try:
        await moderation.check(texts=[record.get("story_text", ""), record.get("title", "")])
    except moderation.ContentRefused:
        await registry.store().update_story(story_id, status="rejected", review_note="Did not pass the content check.")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This story cannot be shared with other families.")
    return await registry.store().update_story(
        story_id, status="pending", consent=True, consent_at=_now(), review_note="", reports=[]
    )


async def unpublish(story_id: str, user: User) -> Dict[str, Any]:
    await _owned(story_id, user, reviewer_ok=True)  # a reviewer may take a story down too
    return await registry.store().update_story(story_id, status="private", published_at=None)


def public_view(record: Dict[str, Any]) -> Dict[str, Any]:
    out = {k: record.get(k) for k in PUBLIC_FIELDS}
    out["pictures"] = {"cover": (record.get("pictures") or {}).get("cover")} if record.get("pictures") else {}
    return out


async def community(language: Optional[str] = None, limit: int = 40) -> List[Dict[str, Any]]:
    items = await registry.store().stories_by_status("published", limit=200)
    if language:
        items = [r for r in items if r.get("language") == language]
    return [public_view(r) for r in items[:limit]]


async def report(story_id: str, user: Optional[User], reason: str) -> None:
    record = await registry.store().get_story(story_id)
    if not record or record["status"] != "published":
        return
    reports = list(record.get("reports") or [])
    reports.append({"at": _now(), "by": user.id if user else "anon", "reason": reason[:300]})
    fields: Dict[str, Any] = {"reports": reports}
    if len(reports) >= REPORTS_TO_HIDE:
        fields["status"] = "pending"  # hidden until someone looks at it
        fields["review_note"] = f"Hidden after {len(reports)} reports."
    await registry.store().update_story(story_id, **fields)
    logger.warning("Story %s reported (%d): %s", story_id, len(reports), reason[:80])


async def review_queue() -> List[Dict[str, Any]]:
    return await registry.store().stories_by_status("pending", limit=100)


async def review(story_id: str, decision: str, note: str) -> Dict[str, Any]:
    if decision == "approve":
        fields = {"status": "published", "published_at": _now(), "review_note": note, "reports": []}
    else:
        fields = {"status": "rejected", "published_at": None, "review_note": note}
    record = await registry.store().update_story(story_id, **fields)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That story is not here any more.")
    return record
