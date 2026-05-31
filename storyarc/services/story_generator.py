import boto3
import json
import asyncio
from typing import Dict, Any, List
import logging
import config
from utils.prompt_templates import build_story_prompt
from models.story_model import StoryGenerationRequest, StoryMetadata, StoryGenerationResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StoryGenerator:
    def __init__(self):
        # Initialize AWS Bedrock client
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = config.BEDROCK_MODEL_ID
        
    async def generate_story(self, request_data: StoryGenerationRequest) -> StoryGenerationResponse:
        """Generate a story using Amazon Bedrock with Claude 3 model."""
        # Build prompt from the request data
        prompt = build_story_prompt(request_data)
          # Create the request body for Bedrock Claude
        # Modified for correct Claude parameters in Bedrock
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": 0.7,
            "system": "You are a creative storyteller who crafts engaging and emotionally resonant stories. Respond with only the story text, without any meta-commentary, narration instructions, or text formatting explanations. Do not include phrases like '*clears throat*' or '*speaking in a tone*'. Just tell the story directly as if you are the narrator speaking to the audience. Always write a COMPLETE story with a proper beginning, middle, and ending. Never cut the story short.",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        
        # Try the following model IDs if the default doesn't work
        # anthropic.claude-3-sonnet-20240229-v1:0
        # anthropic.claude-3-opus-20240229-v1:0
        # anthropic.claude-instant-v1
        # anthropic.claude-v2
        
        try:
            # Log the request for debugging
            logger.info(f"Using Bedrock model ID: {self.model_id}")
            logger.info(f"AWS Region: {config.AWS_REGION}")
            logger.info(f"AWS Access Key ID: {config.AWS_ACCESS_KEY_ID[:4]}... (partial)")
            logger.info(f"Request body structure: {json.loads(body).keys()}")
            
            # Invoke the model using the synchronous API (we'll run it in an executor)
            loop = asyncio.get_event_loop()
            logger.info(f"Calling AWS Bedrock with model: {self.model_id}")
            
            # Check if the modelId exists in available models
            try:
                bedrock = boto3.client('bedrock', region_name=config.AWS_REGION)
                foundation_models = bedrock.list_foundation_models()
                model_ids = [model.get('modelId') for model in foundation_models.get('modelSummaries', [])]
                logger.info(f"Available models: {model_ids}")
            except Exception as model_error:
                logger.warning(f"Could not list available models: {str(model_error)}")
                
            response = await loop.run_in_executor(
                None,
                lambda: self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=body
                )
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read().decode('utf-8'))
            
            # Extract story text from response - structure is different in Bedrock
            story_text = response_body['content'][0]['text']
            
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
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error generating story with Bedrock: {str(e)}\nDetails:\n{error_details}")
            
            # Try to get available models for troubleshooting
            try:
                bedrock = boto3.client('bedrock', 
                                      region_name=config.AWS_REGION,
                                      aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)
                logger.error("Attempting to list available models...")
                models = bedrock.list_foundation_models()
                avail_models = [m.get('modelId') for m in models.get('modelSummaries', [])]
                logger.error(f"Available models: {avail_models}")
                
                if 'anthropic.claude' in str(avail_models):
                    claude_models = [m for m in avail_models if 'anthropic.claude' in m]
                    logger.error(f"Available Claude models: {claude_models}")
                    logger.error("Try using one of these model IDs instead")
            except Exception as model_error:
                logger.error(f"Could not list models: {str(model_error)}")
                
            raise Exception(f"Failed to generate story: {str(e)}")

# Create a singleton instance
story_generator = StoryGenerator()