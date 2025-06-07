from fastapi import APIRouter, HTTPException, status
import uuid
from pydantic import BaseModel
from typing import Dict, Optional

router = APIRouter()

# Simple in-memory storage for sessions (would use a proper database in production)
active_sessions = {}

class UserSession(BaseModel):
    user_id: str
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    message: str

@router.post(
    "/create",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user session",
    description="Create a new session for a user, generating a user_id if not already existing."
)
async def create_session():
    """
    Create a new user session with a unique user_id and session_id.
    """
    try:
        # Generate a new user_id and session_id
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        # Store the session
        active_sessions[session_id] = user_id
        
        return SessionResponse(
            session_id=session_id,
            user_id=user_id,
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get(
    "/validate/{session_id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Validate a user session",
    description="Validate if a session ID is active and return the associated user ID."
)
async def validate_session(session_id: str):
    """
    Validate if a session ID is active and return the associated user ID.
    
    - **session_id**: The session ID to validate
    """
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return {
        "user_id": active_sessions[session_id],
        "message": "Session is valid"
    }

@router.delete(
    "/end/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="End a user session",
    description="End an active user session by session ID."
)
async def end_session(session_id: str):
    """
    End an active user session.
    
    - **session_id**: The session ID to end
    """
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Remove the session
    user_id = active_sessions.pop(session_id)
    
    return {
        "message": f"Session ended for user {user_id}"
    }
