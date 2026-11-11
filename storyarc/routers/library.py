from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from services import library_service
from services.auth import User, current_user

# ---- /library: a family's own stories ---------------------------------------------------------
library = APIRouter()


class PublishRequest(BaseModel):
    consent: bool = Field(False, description="The grown-up confirms the story, and any family pictures in it, may be shown to everyone")


@library.get("/mine", summary="All of this family's stories, newest first")
async def my_stories(user: User = Depends(current_user)) -> List[Dict[str, Any]]:
    return await library_service.mine(user)


@library.post("/{story_id}/publish", summary="Ask to share a story with everyone (goes to review)")
async def publish(story_id: str, body: PublishRequest, user: User = Depends(current_user)):
    return await library_service.publish(story_id, user, body.consent)


@library.post("/{story_id}/unpublish", summary="Take a story off the community shelf")
async def unpublish(story_id: str, user: User = Depends(current_user)):
    return await library_service.unpublish(story_id, user)


@library.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a story for good")
async def delete(story_id: str, user: User = Depends(current_user)):
    await library_service.delete(story_id, user)


# ---- /community: stories families chose to share; free to listen -----------------------------------
community = APIRouter()


class ReportRequest(BaseModel):
    reason: str = Field("", max_length=300)


@community.get("", summary="Published stories (covers only)")
async def shelf(language: Optional[str] = Query(None), limit: int = Query(40, le=100)):
    return await library_service.community(language, limit)


@community.get("/{story_id}", summary="One published story with its recording and pictures")
async def one(story_id: str):
    record = await library_service.get(story_id, None)
    record = dict(record)
    record.pop("reports", None)
    record.pop("owner_id", None)
    return record


@community.post("/{story_id}/report", status_code=status.HTTP_202_ACCEPTED, summary="Flag a story for review")
async def report(story_id: str, body: ReportRequest, user: User = Depends(current_user)):
    await library_service.report(story_id, user, body.reason)
    return {"message": "Thank you. Someone will look at it."}


# ---- /admin: the review queue ----------------------------------------------------------------
admin = APIRouter()


async def require_admin(user: User = Depends(current_user)) -> User:
    if not library_service.is_admin(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reviewers only.")
    return user


class ReviewRequest(BaseModel):
    decision: str = Field(..., regex="^(approve|reject)$")
    note: str = Field("", max_length=300)


class CreditsRequest(BaseModel):
    user_id: str
    credits: int = Field(..., ge=-1000, le=1000)


@admin.get("/review", summary="Stories waiting for a decision")
async def queue(_: User = Depends(require_admin)):
    return await library_service.review_queue()


@admin.post("/review/{story_id}", summary="Approve or reject a story")
async def decide(story_id: str, body: ReviewRequest, _: User = Depends(require_admin)):
    return await library_service.review(story_id, body.decision, body.note)


@admin.post("/credits", summary="Add (or remove) story credits for a family")
async def credits(body: CreditsRequest, _: User = Depends(require_admin)):
    return await library_service.grant_credits(body.user_id, body.credits)
