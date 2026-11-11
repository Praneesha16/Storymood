import boto3
from typing import Dict, Any, List, Optional
import config
import logging

logger = logging.getLogger(__name__)

class DynamoDBClient:
    def __init__(self):
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION
            )
            self.stories_table = self.dynamodb.Table(config.STORIES_TABLE)
            self.users_table = self.dynamodb.Table(config.USERS_TABLE)
            self.is_connected = True
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
            self.is_connected = False
    
    async def create_tables_if_not_exist(self) -> None:
        """Create the required DynamoDB tables if they don't exist."""
        if not self.is_connected:
            logger.warning("DynamoDB client is not connected. Tables will not be created.")
            return
            
        try:
            existing_tables = self.dynamodb.meta.client.list_tables()['TableNames']
            
            if config.STORIES_TABLE not in existing_tables:
                self.dynamodb.create_table(
                    TableName=config.STORIES_TABLE,
                    KeySchema=[
                        {'AttributeName': 'story_id', 'KeyType': 'HASH'},
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'story_id', 'AttributeType': 'S'},
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'UserIdIndex',
                            'KeySchema': [
                                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        },
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
            
            if config.USERS_TABLE not in existing_tables:
                self.dynamodb.create_table(
                    TableName=config.USERS_TABLE,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            
    async def save_story(self, story_data: Dict[str, Any]) -> str:
        """Save a story to DynamoDB."""
        if not self.is_connected:
            logger.warning("DynamoDB client is not connected. Cannot save story.")
            return story_data.get('story_id', '')
        
        try:
            self.stories_table.put_item(Item=story_data)
            return story_data['story_id']
        except Exception as e:
            logger.error(f"Error saving story: {str(e)}")
            return story_data.get('story_id', '')

    async def get_user_stories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all stories for a specific user."""
        if not self.is_connected:
            logger.warning("DynamoDB client is not connected. Cannot retrieve user stories.")
            return []
        
        try:
            response = self.stories_table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error retrieving user stories: {str(e)}")
            return []
    
    async def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific story by ID."""
        if not self.is_connected:
            logger.warning("DynamoDB client is not connected. Cannot retrieve story.")
            return None
        
        try:
            response = self.stories_table.get_item(Key={'story_id': story_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Error retrieving story: {str(e)}")
            return None

# Create a singleton instance
dynamodb_client = DynamoDBClient()