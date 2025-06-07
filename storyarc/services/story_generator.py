from anthropic import AsyncAnthropic
from typing import Dict, Any, List
import logging
import config
from utils.prompt_templates import build_story_prompt
from models.story_model import StoryGenerationRequest, StoryMetadata, StoryGenerationResponse

logger = logging.getLogger(__name__)

class StoryGenerator:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        
    async def generate_story(self, request_data: StoryGenerationRequest) -> StoryGenerationResponse:
        """Generate a story using Anthropic's Claude 3 model based on the provided parameters."""
        # Build prompt from the request data
        prompt = build_story_prompt(request_data)
        
        # Make API call to Anthropic Claude 3
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",  # Using Claude 3 Haiku (more affordable)
            max_tokens=1000,
            temperature=0.7,
            system="You are a creative storyteller who crafts engaging and emotionally resonant stories.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract story text from response
        story_text = response.content[0].text
        
        # Estimate duration (roughly 2 minutes per 1500 characters as a heuristic)
        char_count = len(story_text)
        estimated_minutes = max(1, round(char_count / 1500 * 2))
        estimated_duration = f"{estimated_minutes} minutes"
        
        # Extract character names from the request
        character_names = [char.name for char in request_data.custom_characters] if request_data.custom_characters else []
          # Create metadata
        meta = StoryMetadata(
            estimated_duration=estimated_duration,
            story_type=request_data.story_type,
            mood=request_data.mood,
            narrator_style=request_data.narrator_style,
            language=request_data.language,
            characters=character_names
        )
        
        # Return response
        return StoryGenerationResponse(
            story_text=story_text,
            meta=meta
        )

# Create a singleton instance
story_generator = StoryGenerator()
