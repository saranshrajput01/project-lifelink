"""
S3 Storage service — handles file upload/download to MinIO/AWS S3.
"""

import uuid
from datetime import datetime, timezone

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import get_settings

settings = get_settings()


def get_s3_client():
    """Create an S3 client (works with MinIO, AWS S3, and Supabase Storage).

    Path-style addressing + signature v4 are required for MinIO and Supabase's
    S3-compatible endpoint; AWS S3 accepts them too, so we always set them.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def ensure_bucket_exists():
    """Create the storage bucket if it doesn't exist."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except ClientError:
        client.create_bucket(Bucket=settings.S3_BUCKET_NAME)


def generate_s3_key(patient_id: str, filename: str) -> str:
    """Generate a unique S3 key for a file: patients/{id}/2026/07/{uuid}_{filename}."""
    now = datetime.now(timezone.utc)
    unique_id = uuid.uuid4().hex[:8]
    return f"patients/{patient_id}/{now.year}/{now.month:02d}/{unique_id}_{filename}"


async def upload_file_to_s3(
    file_content: bytes, s3_key: str, content_type: str
) -> bool:
    """Upload file bytes to S3/MinIO. Returns True on success."""
    client = get_s3_client()
    try:
        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
        )
        return True
    except ClientError:
        return False


def get_download_url(s3_key: str, expires_in: int = 3600) -> str:
    """Generate a pre-signed download URL (valid for 1 hour by default)."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
        ExpiresIn=expires_in,
    )


def get_file_from_s3(s3_key: str) -> bytes | None:
    """Download file bytes from S3/MinIO. Returns None on failure."""
    client = get_s3_client()
    try:
        resp = client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
        return resp["Body"].read()
    except ClientError:
        return None
