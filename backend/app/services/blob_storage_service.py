import os
from azure.storage.blob import BlobServiceClient


class BlobStorageService:
    def __init__(self):
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER")

        if not connection_string or not container_name:
            raise ValueError("Azure Blob Storage configuration missing")

        self.client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container = self.client.get_container_client(container_name)

    def upload_file(self, file_stream, filename, content_type):
        blob_client = self.container.get_blob_client(filename)

        blob_client.upload_blob(
            file_stream,
            overwrite=True,
            content_type=content_type
        )

        return blob_client.url
