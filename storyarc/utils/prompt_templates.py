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
    """Build the complete prompt for story generation based on user input."""    # Base prompt with language-specific considerations
    if data.language.value == "Hindi":
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in authentic {data.language.value} language (not transliterated), narrated in the style of a {data.narrator_style.value}. Use natural Hindi expressions, idioms, and phrasing that would be used by native Hindi speakers."
    elif data.language.value == "Telugu":
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in authentic {data.language.value} language (not transliterated), narrated in the style of a {data.narrator_style.value}. Use natural Telugu expressions, idioms, and phrasing that would be used by native Telugu speakers."
    elif data.language.value == "Tamil":
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in authentic {data.language.value} language (not transliterated), narrated in the style of a {data.narrator_style.value}. Use natural Tamil expressions, idioms, and phrasing that would be used by native Tamil speakers."
    elif data.language.value == "Malayalam":
        prompt = f"Tell me a {data.mood.value} {data.story_type.value} story in authentic {data.language.value} language (not transliterated), narrated in the style of a {data.narrator_style.value}. Use natural Malayalam expressions, idioms, and phrasing that would be used by native Malayalam speakers."
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
    elif data.language.value == "Tamil":
        prompt += "\n\nUse authentic Tamil vocabulary and sentence structures. Incorporate culturally relevant references and expressions that would resonate with Tamil speakers. Include traditional Tamil storytelling elements where appropriate."
    elif data.language.value == "Malayalam":
        prompt += "\n\nUse authentic Malayalam vocabulary and sentence structures. Incorporate culturally relevant references and expressions that would resonate with Malayalam speakers. Include Kerala cultural elements where appropriate."
      # Add standard closing guidance
    prompt += "\n\nMake it engaging, emotionally vivid, and age-inclusive. Write a COMPLETE story with a clear beginning, middle, and satisfying ending. Do not leave the story unfinished. Write the story directly without any meta-commentary, narration instructions, or roleplay indicators (such as '*speaking in a tone*' or '*clears throat*'). Just tell the story directly as if you are the narrator."
    
    return prompt

def build_narration_prompt(story_text: str, narrator_style: NarratorStyle, language: str = "English") -> str:
    """
    Return the story text with subtle language-specific processing to enhance pronunciation.
    
    Azure TTS voices are configured with appropriate settings in the VoiceGenerator class
    through the voice_settings mapping, which controls style, rate, and pitch.
    
    For non-English languages, this function applies minimal but important text processing
    to improve the natural pronunciation and rhythm.
    
    No instructions are added to the text as they would be read aloud.
    
    The language parameter can now be either a Language enum value or a direct string.
    """
    # Get the raw language value (e.g., "Hindi", "Telugu")
    # Handle both string and enum cases
    lang_value = language.value if hasattr(language, 'value') else language
    
    # Basic cleanup for all languages
    story_text = story_text.replace("  ", " ")
    story_text = story_text.replace(" ,", ",").replace(" .", ".")
    
    # Language-specific processing
    if lang_value == "Hindi":
        # Add subtle pronunciation helps for complex words (no direct instructions)
        story_text = story_text.replace("।", "। ")
        
    elif lang_value == "Telugu":
        # Telugu-specific processing
        # Add appropriate spacing for Telugu punctuation
        pass
    
    elif lang_value == "Tamil":
        # Tamil-specific processing
        story_text = story_text.replace(".", ". ")
        
    elif lang_value == "Malayalam":
        # Malayalam-specific processing
        story_text = story_text.replace(".", ". ")
        story_text = story_text.replace(".", ". ")
        
        # Add subtle pronunciation helps for complex words
        # These help the TTS model with appropriate Telugu pacing
        story_text = story_text.replace(".", ". ")
        
    # Return the processed text - always just text without explicit voice instructions
    # All voice characteristics are handled by voice selection and settings
    return story_text