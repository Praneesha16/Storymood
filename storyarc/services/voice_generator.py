import httpx
import config
import os
import uuid
from typing import Dict, Any, Optional
from models.story_model import NarrationRequest, NarrationResponse, Language
from utils.prompt_templates import build_narration_prompt

class VoiceGenerator:
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = config.TTS_VOICE_ID
          # Map languages to appropriate models
        self.language_models = {
            "English": "eleven_monolingual_v1",
            "Hindi": "eleven_multilingual_v2", 
            "Telugu": "eleven_multilingual_v2"
        }
          # Language-specific accent settings - used to guide voice configuration, not spoken aloud
        self.accent_instructions = {
            "Hindi": "Hindi",
            "Telugu": "Telugu",
            "English": ""
        }
        
        # Map languages to voices with different narrator styles
        self.voice_mapping = {
            "English": {
                "Wise Grandparent": "21m00Tcm4TlvDq8ikWAM",  # Rachel, warm female voice for grandmother
                "Child's Voice": "AZnzlk1XvdvUeBnXmlld",     # Domi, enthusiastic voice for child
                "Celebrity-style": "EXAVITQu4vr4xnSDxMaL",   # Bella, professional voice
                "Neutral AI": "MF3mGyEYCl7XYWbV9V6O",        # Adam, neutral voice
                "Indian English": "TxGEqnHWrfWFTfGW9XjX",    # Josh voice with Indian English accent settings
                "Self": self.default_voice_id
            },
            "Hindi": {
                "Default": "IKne3meq5aSn9XLyUdCD",    # Charlie, optimized for Hindi
                "Female": "XrExE9yKIg1WjnnlVkGX",     # Grace, smoother for Hindi
                "Male": "AIwZZrFshXhxPu3uLySo",       # Thomas, clearer for Hindi
                "Wise Grandparent": "bVMeCyTHy58xNoL34h3p",  # Daniel, warm voice for Hindi storytelling
                "Child's Voice": "jsCqWAovK2LkecY7zXl4",     # Antoni (child-like)
                "Celebrity-style": "t0jbNlBVZ17f02VDIeMI",   # Callum (professional)
                "Neutral AI": "flq6f7yk4E4fJM5XTYuZ",        # Fin (neutral)
                "Indian English": "TxGEqnHWrfWFTfGW9XjX",    # Josh with settings
                "Self": self.default_voice_id
            },
            "Telugu": {
                "Default": "GBv7mTt0atIp3Br8iCZE",    # Glinda, better for Telugu
                "Female": "jBpfuIE2acCO8z3wKNLl",     # Scarlett, more expressive for Telugu
                "Male": "onwK4e9ZLuTAKqWW3q9Q",       # Matthew, clearer for Telugu
                "Wise Grandparent": "GDe4X2T6B9kOAMn6lOH0",  # Jeremy, warm voice
                "Child's Voice": "jsCqWAovK2LkecY7zXl4",     # Antoni (child-like)
                "Celebrity-style": "t0jbNlBVZ17f02VDIeMI",   # Callum (professional)
                "Neutral AI": "SOYHLrjzK2X1ezoPC6cr",        # Sarah (neutral)
                "Indian English": "TxGEqnHWrfWFTfGW9XjX",    # Josh with settings
                "Self": self.default_voice_id
            }
        }        # Voice settings optimized for different narrator styles and languages
        self.voice_settings = {
            # General style settings
            "Wise Grandparent": {
                "stability": 0.45,         # Moderate for natural variations but still stable
                "similarity_boost": 0.75,  # Better stability for free tier voices
                "style": 0.5              # Medium expressiveness for storytelling
            },
            "Child's Voice": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.6
            },
            "Celebrity-style": {
                "stability": 0.65,
                "similarity_boost": 0.8, 
                "style": 0.5
            },
            "Neutral AI": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.3
            },
            "Indian English": {
                "stability": 0.4,          # Lower stability for more natural accent variations
                "similarity_boost": 0.65,  # Lower for more character/accent
                "style": 0.7              # Higher expressiveness for more distinct Indian English style
            },
            "Self": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0
            }
        }
          # Language-specific voice settings
        self.language_settings = {
            "English": {
                "stability": 0.65,
                "similarity_boost": 0.75,
                "style": 0.35
            },
            "Hindi": {
                "stability": 0.35,         # Lower stability for more natural Hindi speech patterns
                "similarity_boost": 0.6,   # Lower to emphasize the uniqueness of Hindi pronunciation
                "style": 0.8,              # Higher style for more characteristic Hindi accent
                "use_speaker_boost": True  # Boost speaker recognition for Hindi
            },
            "Telugu": {
                "stability": 0.3,          # Lower stability for Telugu's distinctive rhythm and intonation
                "similarity_boost": 0.55,  # Lower to allow for authentic Telugu character
                "style": 0.85,             # Higher style to enhance the Telugu accent and flow
                "use_speaker_boost": True  # Boost speaker recognition for Telugu
            }
        }
        # Ensure audio directory exists
        os.makedirs(config.AUDIO_FILES_DIR, exist_ok=True)
    
    def get_audio_file_path(self, filename: str) -> str:
        """Get the full path to an audio file in the audio directory."""
        return os.path.join(config.AUDIO_FILES_DIR, filename)
    
    def check_audio_exists(self, filename: str) -> bool:
        """Check if an audio file exists in the audio directory."""
        file_path = self.get_audio_file_path(filename)
        return os.path.exists(file_path)
        
    async def narrate_story(self, request: NarrationRequest) -> NarrationResponse:
        """Convert text to speech using ElevenLabs API and save audio locally."""
        language = request.language.value
        
        # Select the appropriate voice based on language and narrator style
        if language in self.voice_mapping:
            # Get the voices for this language
            language_voices = self.voice_mapping[language]
            
            # Check if the requested narrator style is available for this language
            if request.narrator_style.value in language_voices:
                voice_id = language_voices[request.narrator_style.value]
            else:
                # If the specific style is not available, use Default or first available voice
                voice_id = language_voices.get("Default", list(language_voices.values())[0])
        else:
            # Fallback to default voice if language not supported
            voice_id = self.default_voice_id
          # Get the optimized voice settings for the selected narrator style
        style_settings = self.voice_settings.get(
            request.narrator_style.value,
            {"stability": 0.75, "similarity_boost": 0.75, "style": 0.5}
        )
        
        # Get language-specific settings
        lang_settings = self.language_settings.get(
            language,
            {"stability": 0.65, "similarity_boost": 0.75, "style": 0.5}
        )
        
        # Combine style and language settings, prioritizing language settings
        voice_settings = {
            "stability": lang_settings.get("stability", style_settings.get("stability")),
            "similarity_boost": lang_settings.get("similarity_boost", style_settings.get("similarity_boost")),
            "style": lang_settings.get("style", style_settings.get("style"))
        }
          # Get the processed story text (no instructions added since they would be read aloud)
        story_text_to_narrate = build_narration_prompt(request.story_text, request.narrator_style, request.language)
          # Instead of adding accent instructions to the narrated text (which would be read out loud),
        # we'll use them to modify the voice settings for better language adaptation
        if language != "English" and language in self.accent_instructions:
            # Adjust voice settings further based on language rather than adding text instructions
            if language == "Telugu":
                voice_settings["style"] = 0.9  # Maximize style for authentic Telugu accent
            elif language == "Hindi":
                voice_settings["style"] = 0.85  # High style for Hindi expressiveness
        
        # Select the appropriate model for the language
        model_id = self.language_models.get(language, "eleven_multilingual_v2")
        
        # Force multilingual model for non-English content
        if language != "English":
            model_id = "eleven_multilingual_v2"
        
        # Add speaker_boost parameter for languages that need it
        if language in ["Hindi", "Telugu"] and "use_speaker_boost" in lang_settings:
            voice_settings["use_speaker_boost"] = lang_settings["use_speaker_boost"]
        
        # Prepare the request payload        # For non-English content, we can add some special voice settings
        # that will help the model understand it's supposed to use that language
        if language != "English":
            # Using the optimize_streaming_latency parameter with a value of 0 can sometimes improve
            # pronunciation for non-English languages on ElevenLabs API
            voice_settings["optimize_streaming_latency"] = 0
        
        payload = {
            "text": story_text_to_narrate,
            "model_id": model_id,  # Use appropriate model for the language
            "voice_settings": voice_settings
        }
        
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        # Create a unique filename for the audio file
        filename = f"{uuid.uuid4()}.mp3"
        file_path = self.get_audio_file_path(filename)
        
        # Make the API call to ElevenLabs
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/text-to-speech/{voice_id}/stream",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: {response.text}")
            
            # Write the audio data to a file
            with open(file_path, "wb") as f:
                f.write(response.content)
            # Generate the URL for the audio file
            audio_url = f"/static/audio/{filename}"
            
            return NarrationResponse(audio_url=audio_url)

# Create a singleton instance
voice_generator = VoiceGenerator()