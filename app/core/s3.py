import boto3
from mypy_boto3_s3 import S3Client
from pydantic import BaseModel, Field
from ulid import ULID

from app.core.config import settings
from app.core.utils.validators import ImageContentTypeField

s3_client: S3Client = boto3.client(
    "s3",
    region_name=settings.S3_REGION,
    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
)


class PresignedUrlRequest(BaseModel):
    content_type: ImageContentTypeField = Field(examples=["image/jpeg", "image/png", "image/webp", "image/gif"])


class PresignedUrlResponse(BaseModel):
    upload_url: str
    key: str


def generate_object_key(prefix: str, extension: str) -> str:
    return f"{prefix}/{ULID()}.{extension}"


def generate_object_upload_url(key: str, content_type: str, expires_in: int = 300) -> str:
    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )


def generate_presigned_download_url(key: str, expires_in: int = 300) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=expires_in,
    )


def delete_object(key: str) -> None:
    s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)


def create_presigned_upload_url(request: PresignedUrlRequest, prefix: str) -> PresignedUrlResponse:
    extension = request.content_type.split("/")[-1]
    key = generate_object_key(prefix, extension)
    upload_url = generate_object_upload_url(key=key, content_type=request.content_type)
    return PresignedUrlResponse(upload_url=upload_url, key=key)
