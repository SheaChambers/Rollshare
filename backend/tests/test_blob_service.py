import os
import pytest
from app.services.blob_storage_service import BlobStorageService


def test_blob_service_missing_config():
    os.environ.pop("AZURE_STORAGE_CONNECTION_STRING", None)
    os.environ.pop("AZURE_STORAGE_CONTAINER", None)

    with pytest.raises(ValueError):
        BlobStorageService()
