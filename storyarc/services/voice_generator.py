import os
import uuid
import time
import asyncio
import azure.cognitiveservices.speech as speechsdk
import config
from typing import Dict, Any, Optional
from models.story_model import NarrationRequest, NarrationResponse, Language
from utils.prompt_templates import build_narration_prompt
from langdetect import detect, LangDetectException

class VoiceGenerator:
    def __init__(self):
        self.speech_key = config.AZURE_SPEECH_KEY
        self.speech_region = config.AZURE_SPEECH_REGION
        self.default_voice = "en-US-JennyNeural"
          # Map languages to appropriate voices
        self.voice_mapping = {
            "English": {
                "Wise Grandparent": "en-US-SaraNeural",  # Warm female voice for grandmother
                "Wise Grandfather": "en-US-GuyNeural",   # Warm male voice for grandfather with custom voice ID IFWXLbKqk9omOAs0kRNJ
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
            },
            "Tamil": {
                "Default": "ta-IN-PallaviNeural",        # Default Tamil female voice
                "Female": "ta-IN-PallaviNeural",         # Tamil female voice
                "Male": "ta-IN-ValluvarNeural",          # Tamil male voice
                "Wise Grandparent": "ta-IN-PallaviNeural", # Warm voice for Tamil storytelling
                "Child's Voice": "ta-IN-PallaviNeural",    # Use with style="cheerful"
                "Celebrity-style": "ta-IN-ValluvarNeural",  # Professional Tamil voice
                "Neutral AI": "ta-IN-ValluvarNeural",      # Neutral Tamil voice
                "Indian English": "en-IN-NeerjaNeural",    # Indian English female voice
                "Self": "ta-IN-PallaviNeural"
            },
            "Malayalam": {
                "Default": "ml-IN-SobhanaNeural",        # Default Malayalam female voice
                "Female": "ml-IN-SobhanaNeural",         # Malayalam female voice
                "Male": "ml-IN-SobhanaNeural",           # Same voice (Azure has only female ML voice)
                "Wise Grandparent": "ml-IN-SobhanaNeural", # Warm voice for Malayalam storytelling
                "Child's Voice": "ml-IN-SobhanaNeural",    # Use with style="cheerful"
                "Celebrity-style": "ml-IN-SobhanaNeural",  # Professional Malayalam voice
                "Neutral AI": "ml-IN-SobhanaNeural",       # Neutral Malayalam voice
                "Indian English": "en-IN-NeerjaNeural",    # Indian English female voice
                "Self": "ml-IN-SobhanaNeural"
            }
        }
          # Voice style mappings (style, rate, pitch adjustments)
        self.voice_styles = {
            "Wise Grandparent": {
                "style": "gentle",
                "rate": "-10%",  # Slightly slower
                "pitch": "-5%"   # Slightly lower pitch
            },
            "Wise Grandfather": {
                "style": "calm",
                "rate": "-15%",  # Slower for gravitas
                "pitch": "-10%"  # Deeper voice for grandfather
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
            "Telugu": "te-IN",
            "Tamil": "ta-IN",
            "Malayalam": "ml-IN"
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
        
    def _detect_language(self, text: str) -> Optional[str]:
        """
        Automatically detect the language of the text.
        Returns the language name (English, Hindi, Telugu, etc.) or None if detection fails.
        """
        try:
            # Map of language detection codes to our language enum values
            lang_map = {
                'en': 'English',
                'hi': 'Hindi',
                'te': 'Telugu',
                'ta': 'Tamil',
                'ml': 'Malayalam'
            }
            
            # Detect the language
            detected_code = detect(text)
            
            # Map the detected code to our language enum values
            if detected_code in lang_map:
                return lang_map[detected_code]
            else:
                print(f"Detected language code '{detected_code}' not supported, falling back to English")
                return 'English'
                
        except LangDetectException as e:
            print(f"Language detection failed: {str(e)}, falling back to English")
            return None
    
    def build_ssml(self, text: str, voice_name: str, style_settings: Dict[str, str]) -> str:
        """
        Build SSML document with text, voice and style settings.
        """
        # Extract style settings
        style = style_settings.get("style", "neutral")
        rate = style_settings.get("rate", "+0%")
        pitch = style_settings.get("pitch", "+0%")
        
        # Determine the language code from the voice name
        language_code = "en-US"  # Default
        if "-" in voice_name:
            voice_lang_code = voice_name.split("-")[0] + "-" + voice_name.split("-")[1]
            for lang, code in self.language_codes.items():
                if code == voice_lang_code:
                    language_code = code
                    break
        
        # Check if the voice-style combination is supported
        # Some languages might not support all styles
        use_style_tag = True
        if language_code in ["ml-IN"]:
            # Malayalam might have limited style support
            use_style_tag = (style == "neutral")
            
        # Build the SSML document
        if use_style_tag:
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{language_code}">
                <voice name="{voice_name}">
                    <mstts:express-as style="{style}" styledegree="1">
                        <prosody rate="{rate}" pitch="{pitch}">
                            {text}
                        </prosody>
                    </mstts:express-as>
                </voice>
            </speak>
            """
        else:
            # Simplified SSML for languages with limited style support
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{language_code}">
                <voice name="{voice_name}">
                    <prosody rate="{rate}" pitch="{pitch}">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
        return ssml
    
    async def narrate_story(self, request: NarrationRequest) -> NarrationResponse:
        """Convert text to speech using Azure Cognitive Services Speech SDK and save audio locally."""
        # Auto-detect the language from the story text
        detected_language = self._detect_language(request.story_text)
        
        # Use detected language or fallback to English
        language = detected_language if detected_language else "English"
        
        # For logging purposes
        print(f"Using language: {language}")
        
        # Process the story text - pass the detected language directly instead of from request
        story_text_to_narrate = build_narration_prompt(request.story_text, request.narrator_style, language)
        
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