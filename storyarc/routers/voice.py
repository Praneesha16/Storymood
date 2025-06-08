from fastapi import APIRouter, HTTPException, status, Response
from typing import Dict, Any
import os
from pathlib import Path
import config

from models.story_model import NarrationRequest, NarrationResponse
from services.voice_generator import voice_generator

router = APIRouter()

@router.post(
    "/narrate",
    response_model=NarrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Convert story text to speech with expressive narration",
    description="Convert the provided story text to speech using the specified narrator style. The language is automatically detected from the text content (supports English, Hindi, Telugu, Tamil, and Malayalam)."
)
async def narrate_story(request: NarrationRequest):
    """
    Convert the provided story text to speech and save the audio file locally.
    The language is automatically detected from the text content.
    
    - **story_text**: The text content of the story to narrate (in any supported language: English, Hindi, Telugu, Tamil, and Malayalam)
    - **narrator_style**: The style of narrator voice to use (e.g., Wise Grandparent, Child's Voice)
    
    Returns:
    - **audio_url**: URL path to the generated audio file that can be accessed via the server
    """
    try:
        response = await voice_generator.narrate_story(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to narrate story: {str(e)}"
        )

@router.get(
    "/audio-status/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Check if an audio file exists",
    description="Check if a specific audio file exists on the server."
)
async def check_audio_file(filename: str):
    """
    Check if a specific audio file exists on the server.
    
    - **filename**: Name of the audio file to check
    
    Returns:
    - **exists**: Boolean indicating if the file exists
    - **url**: Full URL path to the audio file if it exists
    """
    try:
        exists = voice_generator.check_audio_exists(filename)
        if exists:
            return {
                "exists": True, 
                "url": f"/static/audio/{filename}"
            }
        else:
            return {"exists": False, "url": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check audio file: {str(e)}"
        )

@router.get(
    "/available-voices",
    status_code=status.HTTP_200_OK,
    summary="List available narrator voices",
    description="Get information about all available narrator voice styles and their characteristics."
)
async def list_available_voices():
    """
    List all available narrator voices with their descriptions.
    
    Returns:
    - Dictionary of available voice styles and their descriptions
    """
    return {
        "Wise Grandparent": "A warm, gentle grandmotherly voice perfect for traditional bedtime stories. Speaks with nurturing tone and wisdom.",
        "Child's Voice": "An enthusiastic child's voice with natural excitement and wonder. Great for playful stories.",
        "Celebrity-style": "A professional narrator with clear articulation and dynamic delivery. Ideal for captivating, performance-like narration.",
        "Neutral AI": "A pleasant, well-modulated voice without strong character traits. Good for informational or educational content.",
        "Indian English": "A voice with authentic Indian English accent and intonation patterns. Includes occasional Indian phrases and expressions for cultural authenticity.",
        "Self": "The default voice option with standard narration qualities."
    }

@router.get(
    "/available-languages",
    status_code=status.HTTP_200_OK,
    summary="List available languages",
    description="Get information about all available languages for narration."
)
async def list_available_languages():
    """
    List all available languages for narration.
    
    Returns:
    - Dictionary of available languages and their descriptions
    """
    return {
        "English": "Standard English narration with various voice options including warm grandmother, child, professional, and neutral styles. Uses eleven_monolingual_v1 model for best quality English pronunciation.",
        "Hindi": "Hindi narration with authentic accent and pronunciation. Features specialized voices optimized for Hindi language patterns, rhythm, and phonetics. Supports multiple narrator styles including storyteller, formal, and conversational.",
        "Telugu": "Telugu narration with native-sounding accent and authentic pronunciation. Includes voices specifically tuned for Telugu's unique sounds and intonation. Multiple narrator styles available for different storytelling approaches.",
        "Tamil": "Tamil narration with authentic accent and natural pronunciation. Features voices optimized for Tamil language characteristics including proper stress patterns and phonetics. Supports both male (ValluvarNeural) and female (PallaviNeural) voice options.",
        "Malayalam": "Malayalam narration with native-sounding voice and authentic pronunciation. Features the SobhanaNeural voice specifically tuned for Malayalam's unique linguistic properties and natural speech patterns."
    }