"""Library records in one DynamoDB table (on-demand billing; pennies at family scale).

Table STORYMOOD_TABLE: partition key `pk` ("story#<id>" or "user#<id>").
Indexes: owner-index (owner_id, created_at) and status-index (status, sort_at) for the shelves.
Created on first start when missing. Needs AWS credentials (see .env) with DynamoDB rights.
Floats are stored as strings in `cues` because DynamoDB rejects Python floats.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Key

import config
from providers.base import StoreProvider

logger = logging.getLogger(__name__)


class DynamoStore(StoreProvider):
    name = "dynamodb"

    def __init__(self) -> None:
        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        )
        self.table = self.dynamodb.Table(config.STORYMOOD_TABLE)
        self._ensure_table()

    def _ensure_table(self) -> None:
        client = self.dynamodb.meta.client
        if config.STORYMOOD_TABLE in client.list_tables()["TableNames"]:
            return
        logger.info("Creating DynamoDB table %s", config.STORYMOOD_TABLE)
        client.create_table(
            TableName=config.STORYMOOD_TABLE,
            BillingMode="PAY_PER_REQUEST",
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "owner_id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "sort_at", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {"IndexName": "owner-index", "KeySchema": [{"AttributeName": "owner_id", "KeyType": "HASH"}, {"AttributeName": "created_at", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}},
                {"IndexName": "status-index", "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}, {"AttributeName": "sort_at", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}},
            ],
        )
        client.get_waiter("table_exists").wait(TableName=config.STORYMOOD_TABLE)

    # DynamoDB cannot store floats or empty strings: round-trip records through JSON text.
    @staticmethod
    def _pack(record: Dict[str, Any], pk: str) -> Dict[str, Any]:
        item = {"pk": pk, "body": json.dumps(record, ensure_ascii=False)}
        for key in ("owner_id", "created_at", "status"):
            if record.get(key):
                item[key] = record[key]
        if record.get("status"):
            item["sort_at"] = record.get("published_at") or record.get("created_at") or ""
        return item

    @staticmethod
    def _unpack(item: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return json.loads(item["body"]) if item else None

    async def put_story(self, record: Dict[str, Any]) -> None:
        await asyncio.to_thread(self.table.put_item, Item=self._pack(record, f"story#{record['id']}"))

    async def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        resp = await asyncio.to_thread(self.table.get_item, Key={"pk": f"story#{story_id}"})
        return self._unpack(resp.get("Item"))

    async def update_story(self, story_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        record = await self.get_story(story_id)
        if not record:
            return None
        record.update(fields)
        await self.put_story(record)
        return record

    async def delete_story(self, story_id: str) -> None:
        await asyncio.to_thread(self.table.delete_item, Key={"pk": f"story#{story_id}"})

    async def stories_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        resp = await asyncio.to_thread(
            self.table.query, IndexName="owner-index", KeyConditionExpression=Key("owner_id").eq(owner_id), ScanIndexForward=False
        )
        return [self._unpack(i) for i in resp.get("Items", [])]

    async def stories_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        resp = await asyncio.to_thread(
            self.table.query, IndexName="status-index", KeyConditionExpression=Key("status").eq(status),
            ScanIndexForward=False, Limit=limit,
        )
        return [self._unpack(i) for i in resp.get("Items", [])]

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        resp = await asyncio.to_thread(self.table.get_item, Key={"pk": f"user#{user_id}"})
        return self._unpack(resp.get("Item"))

    async def put_user(self, record: Dict[str, Any]) -> None:
        await asyncio.to_thread(self.table.put_item, Item={"pk": f"user#{record['id']}", "body": json.dumps(record, ensure_ascii=False)})
