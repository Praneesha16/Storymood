from models.story_model import StoryGenerationRequest, Character, NarratorStyle, Language
from typing import List

def format_characters_for_prompt(characters: List[Character]) -> str:
    """Format the list of characters for inclusion in the prompt."""
    if not characters:
        return ""
        
    character_descriptions = []
    for char in characters:
        character_descriptions.append(f"- {char.name}, a {char.trait} {char.age}-year-old")
    
    return "Include the following characters:\n" + "\n".join(character_descriptions)

def build_story_prompt(data: StoryGenerationRequest) -> str:
    """Build the complete prompt for story generation based on user input."""
    prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in {data.language.value} language, narrated in the style of a {data.narrator_style.value}."
    
    # Add character descriptions if provided
    if data.custom_characters:
        character_text = format_characters_for_prompt(data.custom_characters)
        prompt += f"\n\n{character_text}"
    
    # Add private prompt if provided
    if data.private_prompt:
        prompt += f"\n\nAlso, {data.private_prompt}."
    # Add standard closing guidance
    prompt += "\n\nMake it engaging, emotionally vivid, and age-inclusive."
    
    return prompt

def build_narration_prompt(story_text: str, narrator_style: NarratorStyle, language: Language = Language.ENGLISH) -> str:
    """
    Return the story text without adding any voice instructions.
    
    ElevenLabs voices are already configured with appropriate settings in the VoiceGenerator class
    through the voice_settings mapping, which controls stability, similarity_boost, and style.
    
    The voice selection itself (via voice_mapping) handles the different narrator styles and languages.
    Instructions should NOT be included in the text as they'll be read out loud.
    """
    # Always return just the story text without any instructions
    # Voice characteristics are handled by the voice selection and settings
    return story_text