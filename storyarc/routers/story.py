from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import uuid

from models.story_model import StoryGenerationRequest, StoryGenerationResponse
from services.story_generator import story_generator

router = APIRouter()

@router.post(
    "/generate-story",
    response_model=StoryGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new story",
    description="Generate a new story based on the provided parameters including story type, mood, narrator style, and optional characters and prompts."
)
async def generate_story(request: StoryGenerationRequest):
    """
    Generate a new story based on the provided parameters.
    
    - **story_type**: Category or genre of the story (e.g., Adventure, Moral)
    - **mood**: Desired emotional tone (e.g., Soothing, Intense)
    - **narrator_style**: Narration voice style (e.g., Wise Grandparent, Child's Voice)
    - **custom_characters**: Optional list of character objects with name, age, and trait
    - **private_prompt**: Optional free-form text to include specific elements
    """
    try:
        response = await story_generator.generate_story(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate story: {str(e)}"
        )
