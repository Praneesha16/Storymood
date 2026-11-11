from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from services import auth, library_service, ratelimit

router = APIRouter()


class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)


@router.post("/signup", status_code=status.HTTP_201_CREATED, summary="Create a family account (email + password)")
async def signup(body: SignUpRequest, request: Request):
    """Creates the account in Cognito and activates it, so the grown-up can sign in straight away.
    The password goes to Cognito and is not kept here."""
    ratelimit.hit(request.client.host if request.client else "anon", "signup", 10)
    return await auth.create_account(body.name.strip(), body.email.lower(), body.password)


@router.get("/config", summary="How the app signs people in (no secrets)")
async def auth_config():
    return auth.public_config()


@router.get("/me", summary="The signed-in grown-up, or the guest id")
async def me(user: auth.User = Depends(auth.current_user)):
    return {"id": user.id, "email": user.email, "name": user.name, "guest": user.guest, "allowance": await library_service.allowance(user)}
