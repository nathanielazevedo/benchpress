import asyncio
from functools import lru_cache

from minio import Minio

from core.database import settings


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_ssl,
    )


async def list_instrument_files(instrument_id: str) -> list[dict]:
    """List all objects under {instrument_id}/ and return file metadata."""
    client = get_minio_client()
    bucket = settings.minio_bucket
    prefix = f"{instrument_id}/"

    def _list():
        results = []
        for obj in client.list_objects(bucket, prefix=prefix, recursive=True):
            try:
                stat = client.stat_object(bucket, obj.object_name)
                meta = stat.metadata or {}
            except Exception:
                meta = {}

            uploaded_at = (
                meta.get("x-amz-meta-uploaded-at")
                or meta.get("uploaded-at")
                or (obj.last_modified.isoformat() if obj.last_modified else None)
            )
            original_filename = (
                meta.get("x-amz-meta-original-filename")
                or meta.get("original-filename")
                or obj.object_name.split("/")[-1]
            )

            results.append({
                "object_key":    obj.object_name,
                "filename":      original_filename,
                "instrument_id": instrument_id,
                "uploaded_at":   uploaded_at,
                "size_bytes":    obj.size,
                "content_type":  meta.get("content-type", "application/octet-stream"),
            })
        return results

    return await asyncio.get_event_loop().run_in_executor(None, _list)


def get_object_stream(object_key: str):
    """Return (response, content_type) for streaming a single object."""
    client = get_minio_client()
    response = client.get_object(settings.minio_bucket, object_key)
    content_type = response.headers.get("Content-Type", "application/octet-stream")
    return response, content_type
