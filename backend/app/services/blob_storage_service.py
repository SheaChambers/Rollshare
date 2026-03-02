import os
import tempfile
from datetime import datetime, timedelta
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions
)
import subprocess


class BlobStorageService:
    def __init__(self):
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER")
        self.account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

        if not all([
            connection_string,
            self.container_name,
            self.account_name,
            self.account_key
        ]):
            raise ValueError("Azure Blob Storage configuration missing")

        self.client = BlobServiceClient.from_connection_string(connection_string)
        self.container = self.client.get_container_client(self.container_name)

    # -------------------------------
    # Upload video
    # -------------------------------
    def upload_file(self, file_stream, filename, content_type: str) -> str:
        blob_client = self.container.get_blob_client(filename)

        blob_client.upload_blob(
            file_stream,
            overwrite=True,
            content_type=content_type
        )

        # Return the blob name (NOT public URL)
        return filename

    # -------------------------------
    # Generate secure read URL (SAS)
    # -------------------------------
    def generate_read_url(self, blob_name: str, minutes=120):
        if blob_name.startswith("http"):
            blob_name = blob_name.split(f"{self.container.container_name}/")[-1]
        
        expiry_time = datetime.utcnow() + timedelta(minutes=minutes)

        sas = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time
        )

        return f"{self.container.url}/{blob_name}?{sas}"

    def generate_video_thumbnail(self, video_blob_name):
        """
        Extracts a frame at 1s into the video and uploads it as a thumbnail.
        """
        video_url = self.generate_read_url(video_blob_name, minutes=5)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            thumbnail_path = tmp.name

        thumbnail_blob = video_blob_name.replace(".mp4", ".jpg")

        subprocess.run([
            "ffmpeg",
            "-y",
            "-ss", "00:00:01",
            "-i", video_url,
            "-frames:v", "1",
            "-q:v", "2",
            thumbnail_path
        ], check=True)

        with open(thumbnail_path, "rb") as f:
            self.upload_file(f, thumbnail_blob, "image/jpeg")

        os.remove(thumbnail_path)

        return thumbnail_blob
    
    def delete_blob(self, blob_name: str):
        try: 
            clean_name = blob_name.split('?')[0]

            if "blob.core.windows.net" in clean_name:
                clean_name = clean_name.split(f"{self.container_name}/")[-1]

            blob_client = self.container.get_blob_client(clean_name)
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Azure Delete Error: {e}")
            return False