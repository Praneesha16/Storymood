import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "DmMrRhCDqTkFTcYYCU2A2MWQz2IHCnoB1l0yv9UgORG802jzXI2XJQQJ99BFACYeBjFXJ3w3AAAYACOGJbj7")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# AWS Bedrock Configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# DynamoDB Tables
STORIES_TABLE = os.getenv("STORIES_TABLE", "StoryArc_Stories")
USERS_TABLE = os.getenv("USERS_TABLE", "StoryArc_Users")

# App Settings
TTS_VOICE_ID = os.getenv("TTS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel, a warm female voice
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
APP_ENV = os.getenv("APP_ENV", "development")

# File Storage
AUDIO_FILES_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
AUDIO_FILES_URL_PATH = "/static/audio"

# API Versions
API_V1_PREFIX = "/api/v1"
