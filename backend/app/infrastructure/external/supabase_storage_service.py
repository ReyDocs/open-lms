import os
import uuid
from typing import Optional
from app.application.interfaces.services.i_storage_service import IStorageService
from app.config import settings


class SupabaseStorageService(IStorageService):
    def __init__(
        self,
        supabase_url: Optional[str] = settings.supabase_url,
        supabase_key: Optional[str] = settings.supabase_key,
        upload_dir: str = settings.upload_dir,
    ):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.upload_dir = upload_dir
        self.client = None

        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
            except Exception:
                self.client = None

        if not self.client:
            os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_file(
        self, file_bytes: bytes, filename: str, content_type: str, bucket: str = "attachments"
    ) -> str:
        unique_name = f"{uuid.uuid4()}_{filename}"

        if self.client:
            try:
                storage_bucket = self.client.storage.from_(bucket)
                storage_bucket.upload(
                    path=unique_name,
                    file=file_bytes,
                    file_options={"content-type": content_type},
                )
                return storage_bucket.get_public_url(unique_name)
            except Exception:
                # Fall back to local file storage if Supabase upload fails
                pass

        # Local filesystem storage
        bucket_dir = os.path.join(self.upload_dir, bucket)
        os.makedirs(bucket_dir, exist_ok=True)
        file_path = os.path.join(bucket_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return f"/api/v1/files/{bucket}/{unique_name}"

    async def delete_file(self, file_url: str) -> bool:
        if self.client and file_url.startswith("http"):
            try:
                # parse path and bucket
                parts = file_url.split("/")
                filename = parts[-1]
                bucket = parts[-2]
                self.client.storage.from_(bucket).remove([filename])
                return True
            except Exception:
                return False

        # Local delete
        if "/api/v1/files/" in file_url:
            subpath = file_url.split("/api/v1/files/")[-1]
            local_path = os.path.join(self.upload_dir, subpath)
            if os.path.exists(local_path):
                os.remove(local_path)
                return True
        return False
