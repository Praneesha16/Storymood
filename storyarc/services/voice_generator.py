import os
import uuid
import time
import asyncio
import azure.cognitiveservices.speech as speechsdk
import config
from typing import Dict, Any, Optional
from models.story_model import NarrationRequest, NarrationResponse, Language
from utils.prompt_templates import build_narration_prompt

class VoiceGenerator:
    def __init__(self):
        self.speech_key = config.AZURE_SPEECH_KEY
        self.speech_region = config.AZURE_SPEECH_REGION
        self.default_voice = "en-US-JennyNeural"
        
        # Map languages to appropriate voices
        self.voice_mapping = {
            "English": {
                "Wise Grandparent": "en-US-SaraNeural",  # Warm female voice for grandmother
                "Child's Voice": "en-US-AnaNeural",      # Enthusiastic young voice
                "Celebrity-style": "en-US-JennyNeural",  # Professional voice
                "Neutral AI": "en-US-GuyNeural",         # Neutral voice
                "Indian English": "en-IN-NeerjaNeural",  # Indian English female voice
                "Self": self.default_voice
            },
            "Hindi": {
                "Default": "hi-IN-MadhurNeural",        # Default Hindi male voice
                "Female": "hi-IN-SwaraNeural",          # Hindi female voice
                "Male": "hi-IN-MadhurNeural",           # Hindi male voice
                "Wise Grandparent": "hi-IN-SwaraNeural", # Warm voice for Hindi storytelling
                "Child's Voice": "hi-IN-SwaraNeural",    # Use with style="cheerful"
                "Celebrity-style": "hi-IN-MadhurNeural", # Professional Hindi voice
                "Neutral AI": "hi-IN-MadhurNeural",      # Neutral Hindi voice
                "Indian English": "en-IN-PrabhatNeural", # Indian English male voice
                "Self": "hi-IN-MadhurNeural"
            },
            "Telugu": {
                "Default": "te-IN-SatyaNeural",         # Default Telugu male voice
                "Female": "te-IN-ShrutiNeural",         # Telugu female voice
                "Male": "te-IN-SatyaNeural",            # Telugu male voice
                "Wise Grandparent": "te-IN-ShrutiNeural", # Warm voice for Telugu storytelling
                "Child's Voice": "te-IN-ShrutiNeural",    # Use with style="cheerful"
                "Celebrity-style": "te-IN-SatyaNeural",   # Professional Telugu voice
                "Neutral AI": "te-IN-SatyaNeural",        # Neutral Telugu voice
                "Indian English": "en-IN-NeerjaNeural",   # Indian English female voice
                "Self": "te-IN-SatyaNeural"
            }
        }        # Voice style mappings (style, rate, pitch adjustments)
        self.voice_styles = {
            "Wise Grandparent": {
                "style": "gentle",
                "rate": "-10%",  # Slightly slower
                "pitch": "-5%"   # Slightly lower pitch
            },
            "Child's Voice": {
                "style": "excited",
                "rate": "+10%",  # Faster
                "pitch": "+15%"  # Higher pitch
            },
            "Celebrity-style": {
                "style": "professional",
                "rate": "+0%",   # Normal rate
                "pitch": "+0%"   # Normal pitch
            }, 
            "Neutral AI": {
                "style": "neutral",
                "rate": "+0%",   # Normal rate
                "pitch": "+0%"   # Normal pitch
            },
            "Indian English": {
                "style": "friendly",
                "rate": "-5%",   # Slightly slower for clarity
                "pitch": "+0%"   # Normal pitch
            },
            "Self": {
                "style": "neutral",
                "rate": "+0%",   # Normal rate
                "pitch": "+0%"   # Normal pitch
            }
        }
        
        # Language-specific settings for SSML
        self.language_codes = {
            "English": "en-US",
            "Hindi": "hi-IN",
            "Telugu": "te-IN"
        }        # Ensure audio directory exists
        os.makedirs(config.AUDIO_FILES_DIR, exist_ok=True)
    
    def get_audio_file_path(self, filename: str) -> str:
        """Get the full path to an audio file in the audio directory."""
        return os.path.join(config.AUDIO_FILES_DIR, filename)
    
    def check_audio_exists(self, filename: str) -> bool:
        """Check if an audio file exists in the audio directory."""
        file_path = self.get_audio_file_path(filename)
        return os.path.exists(file_path)
    
    def build_ssml(self, text: str, voice_name: str, style_settings: Dict[str, str]) -> str:
        """
        Build SSML document with text, voice and style settings.
        """
        # Extract style settings
        style = style_settings.get("style", "neutral")
        rate = style_settings.get("rate", "+0%")
        pitch = style_settings.get("pitch", "+0%")
        
        # Build the SSML document
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}" styledegree="1">
                    <prosody rate="{rate}" pitch="{pitch}">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """
        return ssml
    async def narrate_story(self, request: NarrationRequest) -> NarrationResponse:
        """Convert text to speech using Azure Cognitive Services Speech SDK and save audio locally."""
        # Get the narration language
        language = request.language.value
        
        # Process the story text
        story_text_to_narrate = build_narration_prompt(request.story_text, request.narrator_style, request.language)
        
        # Select the appropriate voice based on language and narrator style
        if language in self.voice_mapping:
            # Get the voices for this language
            language_voices = self.voice_mapping[language]
            
            # Check if the requested narrator style is available for this language
            if request.narrator_style.value in language_voices:
                voice_name = language_voices[request.narrator_style.value]
            else:
                # If the specific style is not available, use Default or first available voice
                voice_name = language_voices.get("Default", list(language_voices.values())[0])
        else:
            # Fallback to default voice if language not supported
            voice_name = self.default_voice
        
        # Get style settings for the narrator style
        style_settings = self.voice_styles.get(
            request.narrator_style.value,
            {"style": "neutral", "rate": "+0%", "pitch": "+0%"}
        )
        
        # Create a unique filename for the audio file
        filename = f"{uuid.uuid4()}.mp3"
        file_path = self.get_audio_file_path(filename)
        
        # Configure speech synthesizer
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
        
        # Configure audio output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=file_path)
        
        # Create the speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        try:
            # Build SSML with appropriate voice and style
            ssml = self.build_ssml(story_text_to_narrate, voice_name, style_settings)
            
            # Use the synchronous version which is simpler and less error-prone
            print(f"Starting synthesis for language {language} with voice {voice_name}")
            result = speech_synthesizer.speak_ssml(ssml)
            
            # Check the result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Speech synthesized successfully and saved to {file_path}")
                
                # Small delay to ensure file is fully written and released
                await asyncio.sleep(1)
                
                # Generate the URL for the audio file
                audio_url = f"/static/audio/{filename}"
                
                return NarrationResponse(audio_url=audio_url)
            else:
                error_details = result.error_details if hasattr(result, 'error_details') else "Unknown error"
                raise Exception(f"Speech synthesis failed: {error_details}")
            
        except Exception as ex:
            # Log the error and re-raise
            print(f"Error synthesizing speech with Azure: {str(ex)}")
            
            # Try to clean up partial file if it exists - with retry mechanism
            if os.path.exists(file_path):
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        # Wait a bit before trying to delete
                        await asyncio.sleep(1)
                        os.remove(file_path)
                        print(f"Successfully removed file after {retry+1} attempts")
                        break
                    except Exception as cleanup_ex:
                        print(f"Failed to clean up partial audio file (attempt {retry+1}): {str(cleanup_ex)}")
                        if retry == max_retries - 1:
                            print("Maximum retries reached. Could not clean up file.")
            
            raise ex

# Create a singleton instance
voice_generator = VoiceGenerator()