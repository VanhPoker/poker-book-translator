"""
Cloud Storage Service
Supports: Supabase Storage, Google Cloud Storage, Azure Blob Storage, or Local fallback
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Determine storage provider from env
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "auto").lower()

# Try to import storage libraries
SUPABASE_AVAILABLE = False
GCS_AVAILABLE = False
AZURE_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    pass

try:
    from google.cloud import storage as gcs_storage
    GCS_AVAILABLE = True
except ImportError:
    pass

try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    pass


class StorageService:
    """Service for handling file storage (Supabase, GCS, Azure, or local fallback)"""
    
    def __init__(self):
        self.provider = None
        self.supabase_client: Optional[Client] = None
        self.supabase_bucket = None
        self.gcs_client = None
        self.gcs_bucket = None
        self.azure_client = None
        self.azure_container_name = None
        
        # Auto-detect or use specified provider
        # Priority: Supabase > Azure > GCS > Local
        if STORAGE_PROVIDER == "supabase" or (STORAGE_PROVIDER == "auto" and os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")):
            self._init_supabase()
        elif STORAGE_PROVIDER == "azure" or (STORAGE_PROVIDER == "auto" and os.getenv("AZURE_STORAGE_CONNECTION_STRING")):
            self._init_azure()
        elif STORAGE_PROVIDER == "gcs" or (STORAGE_PROVIDER == "auto" and os.getenv("GCS_BUCKET")):
            self._init_gcs()
        else:
            print("⚠️ No cloud storage configured. Using local storage fallback.")
            self.provider = "local"
    
    def _init_supabase(self):
        """Initialize Supabase Storage"""
        if not SUPABASE_AVAILABLE:
            print("⚠️ supabase not installed. Using local fallback.")
            self.provider = "local"
            return
        
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            self.supabase_bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "books")
            
            self.supabase_client = create_client(url, key)
            
            # Try to create bucket if not exists (will fail silently if exists)
            try:
                self.supabase_client.storage.create_bucket(
                    self.supabase_bucket,
                    options={"public": True}
                )
            except Exception:
                pass  # Bucket already exists
            
            self.provider = "supabase"
            print(f"✅ Connected to Supabase Storage bucket: {self.supabase_bucket}")
        except Exception as e:
            print(f"⚠️ Could not connect to Supabase Storage: {e}")
            self.provider = "local"
    
    def _init_gcs(self):
        """Initialize Google Cloud Storage"""
        if not GCS_AVAILABLE:
            print("⚠️ google-cloud-storage not installed. Using local fallback.")
            self.provider = "local"
            return
        
        try:
            bucket_name = os.getenv("GCS_BUCKET", "book-translator")
            self.gcs_client = gcs_storage.Client()
            self.gcs_bucket = self.gcs_client.bucket(bucket_name)
            self.provider = "gcs"
            print(f"✅ Connected to GCS bucket: {bucket_name}")
        except Exception as e:
            print(f"⚠️ Could not connect to GCS: {e}")
            self.provider = "local"
    
    def _init_azure(self):
        """Initialize Azure Blob Storage"""
        if not AZURE_AVAILABLE:
            print("⚠️ azure-storage-blob not installed. Using local fallback.")
            self.provider = "local"
            return
        
        try:
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            self.azure_container_name = os.getenv("AZURE_STORAGE_CONTAINER", "books")
            
            self.azure_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Create container if not exists
            try:
                self.azure_client.create_container(self.azure_container_name, public_access="blob")
            except Exception:
                pass  # Container already exists
            
            self.provider = "azure"
            print(f"✅ Connected to Azure Blob Storage container: {self.azure_container_name}")
        except Exception as e:
            print(f"⚠️ Could not connect to Azure: {e}")
            self.provider = "local"
    
    def upload_file(self, local_path: str, destination_path: str) -> str:
        """
        Upload a file to storage.
        
        Args:
            local_path: Path to local file
            destination_path: Path in storage (e.g., "books/{id}/result.html")
            
        Returns:
            Public URL of the uploaded file
        """
        if not Path(local_path).exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        if self.provider == "supabase":
            return self._upload_supabase(local_path, destination_path)
        elif self.provider == "gcs":
            return self._upload_gcs(local_path, destination_path)
        elif self.provider == "azure":
            return self._upload_azure(local_path, destination_path)
        else:
            return f"file://{Path(local_path).absolute()}"
    
    def _upload_supabase(self, local_path: str, destination_path: str) -> str:
        """Upload to Supabase Storage"""
        # Determine content type
        content_type = self._get_content_type(destination_path)
        
        with open(local_path, "rb") as f:
            file_data = f.read()
        
        # Upload file (upsert to overwrite if exists)
        self.supabase_client.storage.from_(self.supabase_bucket).upload(
            destination_path,
            file_data,
            {"content-type": content_type, "upsert": "true"}
        )
        
        # Get public URL
        return self.supabase_client.storage.from_(self.supabase_bucket).get_public_url(destination_path)
    
    def _upload_gcs(self, local_path: str, destination_path: str) -> str:
        """Upload to Google Cloud Storage"""
        blob = self.gcs_bucket.blob(destination_path)
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
    
    def _upload_azure(self, local_path: str, destination_path: str) -> str:
        """Upload to Azure Blob Storage"""
        blob_client = self.azure_client.get_blob_client(
            container=self.azure_container_name,
            blob=destination_path
        )
        
        content_type = self._get_content_type(destination_path)
        
        with open(local_path, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )
        
        return blob_client.url
    
    def _get_content_type(self, path: str) -> str:
        """Determine content type from file extension"""
        if path.endswith(".html"):
            return "text/html"
        elif path.endswith(".epub"):
            return "application/epub+zip"
        elif path.endswith(".pdf"):
            return "application/pdf"
        elif path.endswith(".png"):
            return "image/png"
        elif path.endswith(".jpg") or path.endswith(".jpeg"):
            return "image/jpeg"
        return "application/octet-stream"
    
    def upload_directory(self, local_dir: str, destination_prefix: str) -> dict:
        """Upload all files in a directory."""
        urls = {}
        local_path = Path(local_dir)
        
        if not local_path.exists():
            return urls
        
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                destination = f"{destination_prefix}{relative_path}".replace("\\", "/")
                urls[str(relative_path)] = self.upload_file(str(file_path), destination)
        
        return urls
    
    def get_public_url(self, path: str) -> str:
        """Get public URL for a file in storage"""
        if self.provider == "supabase":
            return self.supabase_client.storage.from_(self.supabase_bucket).get_public_url(path)
        elif self.provider == "gcs":
            bucket_name = os.getenv("GCS_BUCKET", "book-translator")
            return f"https://storage.googleapis.com/{bucket_name}/{path}"
        elif self.provider == "azure":
            account_name = self.azure_client.account_name
            return f"https://{account_name}.blob.core.windows.net/{self.azure_container_name}/{path}"
        return f"file://{path}"
    
    def delete_file(self, path: str) -> bool:
        """Delete a file from storage"""
        try:
            if self.provider == "supabase":
                self.supabase_client.storage.from_(self.supabase_bucket).remove([path])
                return True
            elif self.provider == "gcs":
                blob = self.gcs_bucket.blob(path)
                blob.delete()
                return True
            elif self.provider == "azure":
                blob_client = self.azure_client.get_blob_client(
                    container=self.azure_container_name,
                    blob=path
                )
                blob_client.delete_blob()
                return True
        except Exception:
            return False
        return False


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
