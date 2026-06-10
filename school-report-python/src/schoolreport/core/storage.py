"""Google Cloud Storage client for uploading and managing PDFs."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional
from datetime import timedelta
from pathlib import Path

if TYPE_CHECKING:
    from google.cloud import storage
    from google.auth.credentials import Credentials


class StorageError(Exception):
    """Raised when storage operation fails."""

    pass


class GCSClient:
    """Google Cloud Storage client."""

    def __init__(
        self,
        bucket_name: str,
        credentials: Optional[Credentials] = None,
        project_id: Optional[str] = None
    ):
        """Initialize GCS client.

        Args:
            bucket_name: GCS bucket name
            credentials: Optional GCP credentials
            project_id: Optional GCP project ID
        """
        self.bucket_name = bucket_name
        self.credentials = credentials
        self.project_id = project_id
        self._client = None
        self._bucket = None

    def _get_client(self):
        """Get or create storage client.

        Returns:
            Storage client instance
        """
        if self._client is None:
            from google.cloud import storage

            self._client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
        return self._client

    def _get_bucket(self):
        """Get or create bucket reference.

        Returns:
            Bucket instance
        """
        if self._bucket is None:
            client = self._get_client()
            self._bucket = client.bucket(self.bucket_name)
        return self._bucket

    async def upload(
        self,
        path: str,
        content: bytes,
        content_type: str = "application/pdf"
    ) -> str:
        """Upload content to GCS.

        Args:
            path: Path in bucket (e.g., "ATM/2304400-2024.pdf")
            content: File content as bytes
            content_type: MIME type

        Returns:
            Public URL to uploaded file

        Raises:
            StorageError: If upload fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            # Upload in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: blob.upload_from_string(content, content_type=content_type)
            )

            return f"gs://{self.bucket_name}/{path}"
        except Exception as e:
            raise StorageError(f"Upload failed: {e}")

    async def download(self, path: str) -> bytes:
        """Download content from GCS.

        Args:
            path: Path in bucket

        Returns:
            File content as bytes

        Raises:
            StorageError: If download fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                blob.download_as_bytes
            )

            return content
        except Exception as e:
            raise StorageError(f"Download failed: {e}")

    async def exists(self, path: str) -> bool:
        """Check if file exists in GCS.

        Args:
            path: Path in bucket

        Returns:
            True if file exists, False otherwise
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            loop = asyncio.get_event_loop()
            exists = await loop.run_in_executor(
                None,
                blob.exists
            )

            return exists
        except Exception:
            return False

    async def delete(self, path: str) -> bool:
        """Delete file from GCS.

        Args:
            path: Path in bucket

        Returns:
            True if deleted, False if file didn't exist

        Raises:
            StorageError: If deletion fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                blob.delete
            )

            return True
        except Exception as e:
            if "404" in str(e):
                return False
            raise StorageError(f"Deletion failed: {e}")

    async def generate_signed_url(
        self,
        path: str,
        expires_in: int = 3600
    ) -> str:
        """Generate a signed URL for temporary access.

        Args:
            path: Path in bucket
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL

        Raises:
            StorageError: If URL generation fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                lambda: blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(seconds=expires_in),
                    method="GET"
                )
            )

            return url
        except Exception as e:
            raise StorageError(f"Signed URL generation failed: {e}")

    async def get_metadata(self, path: str) -> dict:
        """Get file metadata.

        Args:
            path: Path in bucket

        Returns:
            Metadata dictionary

        Raises:
            StorageError: If operation fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                blob.reload
            )

            return {
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "md5_hash": blob.md5_hash,
            }
        except Exception as e:
            raise StorageError(f"Failed to get metadata: {e}")

    async def upload_file(
        self,
        local_path: Path,
        gcs_path: str,
        content_type: str = "application/pdf"
    ) -> str:
        """Upload a local file to GCS.

        Args:
            local_path: Path to local file
            gcs_path: Destination path in bucket

        Returns:
            Full GCS URI

        Raises:
            StorageError: If upload fails
        """
        content = local_path.read_bytes()
        return await self.upload(gcs_path, content, content_type)


# Alias for backward compatibility
StorageClient = GCSClient
