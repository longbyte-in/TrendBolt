from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from ..config import get_settings


class AzureBlobClient:
    def __init__(self) -> None:
        from azure.storage.blob import BlobServiceClient  # type: ignore

        s = get_settings()
        if s.azure_storage_connection_string:
            self._svc = BlobServiceClient.from_connection_string(s.azure_storage_connection_string)
        else:
            # Fall back to account URL with default credentials (env/AAD)
            account = s.azure_storage_account or ""
            self._svc = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net/")
        self._container = s.azure_storage_container or "posts"

    def upload_bytes(self, name: str, data: bytes, content_type: str = "image/png") -> None:
        container = self._svc.get_container_client(self._container)
        try:
            container.create_container()
        except Exception:
            pass
        blob = container.get_blob_client(name)
        blob.upload_blob(data, overwrite=True, content_settings={"content_type": content_type})

    def generate_sas_url(self, name: str, minutes: int = 60) -> str:
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions  # type: ignore

        s = get_settings()
        account = s.azure_storage_account or ""
        expiry = datetime.utcnow() + timedelta(minutes=minutes)
        token = generate_blob_sas(
            account_name=account,
            container_name=self._container,
            blob_name=name,
            permission=BlobSasPermissions(read=True),
            expiry=expiry,
        )
        return f"https://{account}.blob.core.windows.net/{self._container}/{name}?{token}"


