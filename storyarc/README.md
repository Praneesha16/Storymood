# StoryArc

StoryArc is an AI-powered storytelling app that delivers personalized, emotionally resonant stories across all age groups — from children to seniors.

## Features

- **Story Generation**: Create unique, personalized stories based on user preferences
- **Voice Narration**: Convert stories into spoken narration using realistic AI voices
- **Story Vault**: Save and retrieve user stories
- **Simple Authentication**: Track user sessions

## Tech Stack

- Python 3.10+
- FastAPI (web framework)
- Amazon DynamoDB
- Amazon Bedrock (Claude 3)
- ElevenLabs TTS API
- Uvicorn (ASGI server)

## Project Structure

```
storyarc/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration and environment variables
├── .env                     # Environment variables (not checked into version control)
├── requirements.txt         # Python dependencies
├── routers/                 # API route handlers
│   ├── __init__.py
│   ├── story.py             # Story generation endpoints
│   ├── voice.py             # Voice narration endpoints
│   ├── vault.py             # Story storage endpoints
│   └── session.py           # User session management
├── services/                # Business logic
│   ├── __init__.py
│   ├── story_generator.py   # Story generation service
│   └── voice_generator.py   # Voice synthesis service
├── models/                  # Pydantic models
│   ├── __init__.py
│   └── story_model.py       # Data models for the API
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── prompt_templates.py  # Templates for AI prompts
└── database/                # Database connections
    ├── __init__.py
    └── dynamodb.py          # DynamoDB client
```

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- AWS account with DynamoDB access
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/storyarc.git
   cd storyarc
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys and configuration:
   ```
   # API Keys
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   
   # AWS DynamoDB Configuration
   AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
   AWS_REGION=us-east-1
   
   # DynamoDB Tables
   STORIES_TABLE=StoryArc_Stories
   USERS_TABLE=StoryArc_Users
   
   # App Settings
   TTS_VOICE_ID=default_voice_id
   SECRET_KEY=generate_a_secure_secret_key_for_sessions
   APP_ENV=development
   ```

5. Run the application:
   ```
   python main.py
   ```

   The API will be available at http://localhost:6000

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Story Generation

- `POST /api/v1/story/generate-story` - Generate a new story

### Voice Narration

- `POST /api/v1/voice/narrate` - Convert story text to speech

### Story Vault

- `POST /api/v1/vault/save` - Save a story to the user's vault
- `GET /api/v1/vault/{user_id}` - Get all stories for a user
- `GET /api/v1/vault/story/{story_id}` - Get a specific story by ID

### Session Management

- `POST /api/v1/session/create` - Create a new user session
- `GET /api/v1/session/validate/{session_id}` - Validate a user session
- `DELETE /api/v1/session/end/{session_id}` - End a user session

## License

[MIT License](LICENSE)
