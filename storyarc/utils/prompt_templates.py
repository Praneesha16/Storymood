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
    # Base prompt with language-specific considerations
    if data.language.value == "Hindi":
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in authentic {data.language.value} language (not transliterated), narrated in the style of a {data.narrator_style.value}. Use natural Hindi expressions, idioms, and phrasing that would be used by native Hindi speakers."
    elif data.language.value == "Telugu":
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in authentic {data.language.value} language (not transliterated), narrated in the style of a {data.narrator_style.value}. Use natural Telugu expressions, idioms, and phrasing that would be used by native Telugu speakers."
    else:
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in {data.language.value} language, narrated in the style of a {data.narrator_style.value}."
    
    # Add character descriptions if provided
    if data.custom_characters:
        character_text = format_characters_for_prompt(data.custom_characters)
        prompt += f"\n\n{character_text}"
    
    # Add private prompt if provided
    if data.private_prompt:
        prompt += f"\n\nAlso, {data.private_prompt}."
    
    # Add language-specific guidance for better pronunciation and cultural authenticity
    if data.language.value == "Hindi":
        prompt += "\n\nUse authentic Hindi vocabulary and sentence structures. Incorporate culturally relevant references and expressions that would resonate with Hindi speakers."
    elif data.language.value == "Telugu":
        prompt += "\n\nUse authentic Telugu vocabulary and sentence structures. Incorporate culturally relevant references and expressions that would resonate with Telugu speakers."
      # Add standard closing guidance
    prompt += "\n\nMake it engaging, emotionally vivid, and age-inclusive. Write the story directly without any meta-commentary, narration instructions, or roleplay indicators (such as '*speaking in a tone*' or '*clears throat*'). Just tell the story directly as if you are the narrator."
    
    return prompt

def build_narration_prompt(story_text: str, narrator_style: NarratorStyle, language: Language = Language.ENGLISH) -> str:
    """
    Return the story text with subtle language-specific processing to enhance pronunciation.
    
    ElevenLabs voices are configured with appropriate settings in the VoiceGenerator class
    through the voice_settings mapping, which controls stability, similarity_boost, and style.
    
    For non-English languages, this function applies minimal but important text processing
    to improve the natural pronunciation and rhythm.
    
    No instructions are added to the text as they would be read aloud.
    """
    # Get the raw language value (e.g., "Hindi", "Telugu")
    lang_value = language.value if language else "English"
    
    if lang_value == "Hindi":
        # For Hindi narration, ensure proper spacing between sentences
        # Remove any double spaces which can cause unnatural pauses
        story_text = story_text.replace("  ", " ")
        
        # Ensure correct punctuation spacing for better Hindi rhythm
        story_text = story_text.replace(" ,", ",").replace(" .", ".")
        
        # Add subtle pronunciation helps for complex words (no direct instructions)
        # These won't be read aloud but help the TTS model with pacing
        story_text = story_text.replace("।", "। ")
        
    elif lang_value == "Telugu":
        # For Telugu narration, ensure proper spacing and pacing
        # Remove any double spaces which can cause unnatural pauses
        story_text = story_text.replace("  ", " ")
        
        # Ensure correct punctuation spacing for better Telugu flow
        story_text = story_text.replace(" ,", ",").replace(" .", ".")
        
        # Add subtle pronunciation helps for complex words
        # These help the TTS model with appropriate Telugu pacing
        story_text = story_text.replace(".", ". ")
        
    # Return the processed text - always just text without explicit voice instructions
    # All voice characteristics are handled by voice selection and settings
    return story_text