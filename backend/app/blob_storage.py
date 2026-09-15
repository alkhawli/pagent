from __future__ import annotations

import json
import logging
from typing import Any

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

from app.config import Settings

logger = logging.getLogger(__name__)


class BlobJsonStore:
    """Reads/writes JSON documents in Azure Blob Storage using a single pooled client.

    Uses the storage account connection string when provided (local dev only);
    otherwise authenticates with DefaultAzureCredential, which resolves to the
    Web App's managed identity in Azure.
    """

    def __init__(self, settings: Settings) -> None:
        self._credential: DefaultAzureCredential | None = None
        if settings.azure_storage_connection_string:
            self._client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
        elif settings.azure_storage_account_name:
            self._credential = DefaultAzureCredential()
            account_url = f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
            self._client = BlobServiceClient(account_url, credential=self._credential)
        else:
            raise RuntimeError(
                "Blob storage is not configured. Set AZURE_STORAGE_CONNECTION_STRING (local dev) "
                "or AZURE_STORAGE_ACCOUNT_NAME (managed identity) in .env."
            )
        self._ensured_containers: set[str] = set()

    async def _ensure_container(self, container: str) -> None:
        if container in self._ensured_containers:
            return
        try:
            await self._client.create_container(container)
        except ResourceExistsError:
            pass
        self._ensured_containers.add(container)

    async def read_json(self, container: str, blob_name: str) -> dict[str, Any] | None:
        blob_client = self._client.get_blob_client(container, blob_name)
        try:
            downloader = await blob_client.download_blob(encoding="utf-8")
            content = await downloader.readall()
        except ResourceNotFoundError:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.exception("Corrupt JSON blob %s/%s", container, blob_name)
            return None

    async def write_json(self, container: str, blob_name: str, data: dict[str, Any]) -> None:
        await self._ensure_container(container)
        blob_client = self._client.get_blob_client(container, blob_name)
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        await blob_client.upload_blob(payload, overwrite=True)

    async def close(self) -> None:
        await self._client.close()
        if self._credential is not None:
            await self._credential.close()
