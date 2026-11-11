"""Narration and pictures in an S3 bucket, served through CloudFront (or the bucket's public URL).

Settings: S3_BUCKET, S3_PREFIX (folder inside the bucket), FILES_PUBLIC_BASE (the CloudFront
address, e.g. https://d123.cloudfront.net). Files are stored with a long cache lifetime because
their names are random and never reused. Select with FILES_PROVIDER=s3.
"""
import asyncio

import boto3

import config
from providers.base import FileStore, ProviderError


class S3Files(FileStore):
    name = "s3"

    def __init__(self) -> None:
        if not config.S3_BUCKET:
            raise ProviderError("FILES_PROVIDER=s3 needs S3_BUCKET in storyarc/.env.")
        self.client = boto3.client(
            "s3",
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket = config.S3_BUCKET
        self.prefix = config.S3_PREFIX.strip("/")
        self.base = (config.FILES_PUBLIC_BASE or f"https://{self.bucket}.s3.{config.AWS_REGION}.amazonaws.com").rstrip("/")

    async def save(self, kind: str, filename: str, data: bytes, content_type: str) -> str:
        key = "/".join(p for p in (self.prefix, kind, filename) if p)
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )
        return f"{self.base}/{key}"
