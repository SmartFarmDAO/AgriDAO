"""
Cloud storage management for AgriDAO.
Handles file uploads, downloads, and storage across multiple cloud providers.
"""

import os
import uuid
import mimetypes
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import hashlib
import asyncio
import aiofiles

import boto3
from botocore.exceptions import ClientError
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("cloud_storage")


class CloudStorageProvider:
    """Base class for cloud storage providers."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    async def upload_file(self, file_path: str, destination_path: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload a file to cloud storage."""
        raise NotImplementedError
    
    async def download_file(self, file_path: str, destination_path: str) -> bool:
        """Download a file from cloud storage."""
        raise NotImplementedError
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from cloud storage."""
        raise NotImplementedError
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get a signed URL for file access."""
        raise NotImplementedError
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in cloud storage."""
        raise NotImplementedError


class AWSProvider(CloudStorageProvider):
    """AWS S3 storage provider."""
    
    def __init__(self):
        super().__init__("aws")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
    
    async def upload_file(self, file_path: str, destination_path: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload file to AWS S3."""
        try:
            content_type, _ = mimetypes.guess_type(file_path)
            extra_args = {
                'ContentType': content_type or 'application/octet-stream'
            }
            
            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}
            
            self.s3_client.upload_file(file_path, self.bucket_name, destination_path, ExtraArgs=extra_args)
            
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{destination_path}"
            
            return {
                "provider": "aws",
                "file_url": file_url,
                "file_path": destination_path,
                "bucket": self.bucket_name,
                "etag": self._get_etag(destination_path)
            }
        except ClientError as e:
            logger.error(f"AWS upload failed: {e}")
            raise
    
    async def download_file(self, file_path: str, destination_path: str) -> bool:
        """Download file from AWS S3."""
        try:
            self.s3_client.download_file(self.bucket_name, file_path, destination_path)
            return True
        except ClientError as e:
            logger.error(f"AWS download failed: {e}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from AWS S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            logger.error(f"AWS delete failed: {e}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for AWS S3 file."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"AWS URL generation failed: {e}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in AWS S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    def _get_etag(self, file_path: str) -> Optional[str]:
        """Get ETag for uploaded file."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return response.get('ETag', '').strip('"')
        except ClientError:
            return None


class GCPProvider(CloudStorageProvider):
    """Google Cloud Storage provider."""
    
    def __init__(self):
        super().__init__("gcp")
        self.client = gcs.Client()
        self.bucket_name = settings.GCP_BUCKET_NAME
        self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_file(self, file_path: str, destination_path: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload file to Google Cloud Storage."""
        try:
            blob = self.bucket.blob(destination_path)
            
            content_type, _ = mimetypes.guess_type(file_path)
            blob.content_type = content_type or 'application/octet-stream'
            
            if metadata:
                blob.metadata = metadata
            
            blob.upload_from_filename(file_path)
            
            file_url = f"https://storage.googleapis.com/{self.bucket_name}/{destination_path}"
            
            return {
                "provider": "gcp",
                "file_url": file_url,
                "file_path": destination_path,
                "bucket": self.bucket_name,
                "etag": blob.etag
            }
        except Exception as e:
            logger.error(f"GCP upload failed: {e}")
            raise
    
    async def download_file(self, file_path: str, destination_path: str) -> bool:
        """Download file from Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_path)
            blob.download_to_filename(destination_path)
            return True
        except Exception as e:
            logger.error(f"GCP download failed: {e}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"GCP delete failed: {e}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for Google Cloud Storage file."""
        try:
            blob = self.bucket.blob(file_path)
            url = blob.generate_signed_url(
                expiration=timedelta(seconds=expires_in),
                method='GET'
            )
            return url
        except Exception as e:
            logger.error(f"GCP URL generation failed: {e}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            logger.error(f"GCP file check failed: {e}")
            return False


class AzureProvider(CloudStorageProvider):
    """Azure Blob Storage provider."""
    
    def __init__(self):
        super().__init__("azure")
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_CONTAINER_NAME
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
    
    async def upload_file(self, file_path: str, destination_path: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload file to Azure Blob Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=destination_path
            )
            
            content_type, _ = mimetypes.guess_type(file_path)
            content_settings = None
            if content_type:
                from azure.storage.blob import ContentSettings
                content_settings = ContentSettings(content_type=content_type)
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
            
            if metadata:
                blob_client.set_blob_metadata(metadata)
            
            file_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{destination_path}"
            
            return {
                "provider": "azure",
                "file_url": file_url,
                "file_path": destination_path,
                "container": self.container_name,
                "etag": blob_client.get_blob_properties().etag
            }
        except Exception as e:
            logger.error(f"Azure upload failed: {e}")
            raise
    
    async def download_file(self, file_path: str, destination_path: str) -> bool:
        """Download file from Azure Blob Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=file_path
            )
            
            with open(destination_path, 'wb') as file:
                download_stream = blob_client.download_blob()
                file.write(download_stream.readall())
            
            return True
        except Exception as e:
            logger.error(f"Azure download failed: {e}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Azure Blob Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=file_path
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            logger.error(f"Azure delete failed: {e}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for Azure Blob Storage file."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=file_path
            )
            
            sas_token = blob_client.generate_shared_access_signature(
                permission='read',
                expiry=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            
            return f"{blob_client.url}?{sas_token}"
        except Exception as e:
            logger.error(f"Azure URL generation failed: {e}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in Azure Blob Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=file_path
            )
            blob_client.get_blob_properties()
            return True
        except Exception as e:
            if 'BlobNotFound' in str(e):
                return False
            raise


class CloudStorageManager:
    """Main cloud storage manager with multi-provider support."""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available cloud storage providers."""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.providers["aws"] = AWSProvider()
        
        if settings.GCP_BUCKET_NAME:
            self.providers["gcp"] = GCPProvider()
        
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            self.providers["azure"] = AzureProvider()
        
        if not self.providers:
            logger.warning("No cloud storage providers configured")
    
    async def upload_file(self, file_path: str, destination_path: str = None, 
                         provider: str = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload file to cloud storage with provider selection."""
        if not self.providers:
            raise ValueError("No cloud storage providers available")
        
        if not destination_path:
            destination_path = self._generate_destination_path(file_path)
        
        # Use specified provider or first available
        selected_provider = provider or list(self.providers.keys())[0]
        
        if selected_provider not in self.providers:
            raise ValueError(f"Provider {selected_provider} not available")
        
        # Add metadata
        file_metadata = {
            "original_name": Path(file_path).name,
            "upload_date": datetime.utcnow().isoformat(),
            "file_size": os.path.getsize(file_path),
            "checksum": await self._calculate_checksum(file_path),
            **(metadata or {})
        }
        
        result = await self.providers[selected_provider].upload_file(
            file_path, destination_path, file_metadata
        )
        
        logger.info(
            f"File uploaded successfully",
            provider=selected_provider,
            file_path=destination_path,
            file_size=file_metadata["file_size"]
        )
        
        return {
            **result,
            "metadata": file_metadata,
            "upload_id": str(uuid.uuid4())
        }
    
    async def download_file(self, file_path: str, destination_path: str, 
                           provider: str = None) -> bool:
        """Download file from cloud storage."""
        selected_provider = provider or list(self.providers.keys())[0]
        
        if selected_provider not in self.providers:
            raise ValueError(f"Provider {selected_provider} not available")
        
        result = await self.providers[selected_provider].download_file(file_path, destination_path)
        
        if result:
            logger.info(f"File downloaded successfully", provider=selected_provider, file_path=file_path)
        
        return result
    
    async def delete_file(self, file_path: str, provider: str = None) -> bool:
        """Delete file from cloud storage."""
        selected_provider = provider or list(self.providers.keys())[0]
        
        if selected_provider not in self.providers:
            raise ValueError(f"Provider {selected_provider} not available")
        
        result = await self.providers[selected_provider].delete_file(file_path)
        
        if result:
            logger.info(f"File deleted successfully", provider=selected_provider, file_path=file_path)
        
        return result
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600, 
                          provider: str = None) -> str:
        """Get signed URL for file access."""
        selected_provider = provider or list(self.providers.keys())[0]
        
        if selected_provider not in self.providers:
            raise ValueError(f"Provider {selected_provider} not available")
        
        return await self.providers[selected_provider].get_file_url(file_path, expires_in)
    
    async def file_exists(self, file_path: str, provider: str = None) -> bool:
        """Check if file exists in cloud storage."""
        selected_provider = provider or list(self.providers.keys())[0]
        
        if selected_provider not in self.providers:
            raise ValueError(f"Provider {selected_provider} not available")
        
        return await self.providers[selected_provider].file_exists(file_path)
    
    def _generate_destination_path(self, file_path: str) -> str:
        """Generate destination path for cloud storage."""
        timestamp = datetime.utcnow().strftime('%Y/%m/%d')
        file_name = Path(file_path).name
        unique_id = str(uuid.uuid4())[:8]
        
        # Clean filename for URL safety
        clean_name = "".join(c for c in file_name if c.isalnum() or c in '._-')
        
        return f"uploads/{timestamp}/{unique_id}_{clean_name}"
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5(usedforsecurity=False)
        async with aiofiles.open(file_path, 'rb') as f:
            async for chunk in f:
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available cloud storage providers."""
        return list(self.providers.keys())
    
    async def upload_multiple_files(self, files: List[Dict[str, str]], 
                                  provider: str = None) -> List[Dict[str, Any]]:
        """Upload multiple files concurrently."""
        tasks = []
        for file_info in files:
            task = self.upload_file(
                file_info['file_path'],
                file_info.get('destination_path'),
                provider,
                file_info.get('metadata')
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)


# Global storage manager instance
storage_manager = CloudStorageManager()