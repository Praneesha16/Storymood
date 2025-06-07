from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List
import uuid
from datetime import datetime

from models.story_model import StoryVaultItem, UserStoryList
from database.dynamodb import dynamodb_client

router = APIRouter()

@router.post(
    "/save",
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="Save a story to the user's vault",
    description="Save a generated story along with its metadata and audio URL to the user's personal vault."
)
async def save_story(story: StoryVaultItem):
    """
    Save a story to the user's personal vault.
    
    - **story_id**: Unique identifier for the story (auto-generated if not provided)
    - **user_id**: Identifier for the user
    - **story_text**: The text content of the story
    - **audio_url**: Optional URL to the audio version of the story
    - **meta**: Metadata about the story including type, mood, narrator style, etc.
    - **created_at**: Timestamp for when the story was created (auto-generated if not provided)
    """
    try:
        # Generate a story_id if not provided
        if not story.story_id:
            story.story_id = str(uuid.uuid4())
        
        # Ensure created_at is set
        if not story.created_at:
            story.created_at = datetime.now().isoformat()
            
        # Convert Pydantic model to dict for DynamoDB
        story_dict = story.dict()
        
        # Save to DynamoDB
        await dynamodb_client.save_story(story_dict)
        
        return {"story_id": story.story_id, "message": "Story saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save story: {str(e)}"
        )

@router.get(
    "/{user_id}",
    response_model=UserStoryList,
    status_code=status.HTTP_200_OK,
    summary="Get all stories for a user",
    description="Retrieve all stories saved in the vault for a specific user."
)
async def get_user_stories(user_id: str):
    """
    Retrieve all stories for a specific user from their vault.
    
    - **user_id**: Identifier for the user
    """
    try:
        stories = await dynamodb_client.get_user_stories(user_id)
        return UserStoryList(stories=stories)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stories: {str(e)}"
        )

@router.get(
    "/story/{story_id}",
    response_model=StoryVaultItem,
    status_code=status.HTTP_200_OK,
    summary="Get a specific story by ID",
    description="Retrieve a specific story from the vault by its ID."
)
async def get_story(story_id: str):
    """
    Retrieve a specific story by ID.
    
    - **story_id**: Unique identifier for the story
    """
    try:
        story = await dynamodb_client.get_story(story_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story with ID {story_id} not found"
            )
        return story
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve story: {str(e)}"
        )
