"""GoogleCloudStorage extension classes for MEDIA and STATIC uploads"""
from urllib.parse import urljoin
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting
from google.cloud import storage
import datetime
import requests


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a media file path from MEDIA_URL
    not google generated one."""
    bucket_name = setting('GS_MEDIA_BUCKET_NAME')

    def url(self, name):
        """Gives correct MEDIA_URL and not google generated url."""
        return urljoin(settings.MEDIA_URL, name)
    
    @classmethod
    def get_file_number_of_plays(cls, file_url):
        """Returns number of plays for a file."""
        try:
            # Strip the MEDIA_URL from the file_url to get the blob name
            blob_name = file_url.replace(settings.MEDIA_URL, "")
            
            # Initialize the Google Cloud Storage client
            storage_client = storage.Client()
            bucket = storage_client.bucket(cls.bucket_name)
            blob = bucket.get_blob(blob_name)
            
            objs = {
                "name": blob.name,
                "bucket": blob.bucket.name,
                "storage_class": blob.storage_class,
                "id": blob.id,
                "size": blob.size,
                "updated": blob.updated,
                "generation": blob.generation,
                "metageneration": blob.metageneration,
                "etag": blob.etag,
                "owner": blob.owner,
                "component_count": blob.component_count,
                "crc32c": blob.crc32c,
                "md5_hash": blob.md5_hash,
                "cache_control": blob.cache_control,
                "content_type": blob.content_type,
                "content_disposition": blob.content_disposition,
                "content_encoding": blob.content_encoding,
                "content_language": blob.content_language,
                "metadata": blob.metadata,
                "media_link": blob.media_link,
                "custom_time": blob.custom_time,
            }
            return objs
        except Exception as e:
            print("Error getting file plays: ", e)
            return 0
    
    @classmethod
    def delete_file(cls, file_url):
        """Deletes file from google storage."""
        try:
            blob_name = file_url.replace(settings.MEDIA_URL, "")
            print("blob_name: ", blob_name)
            storage_client = storage.Client()
            bucket = storage_client.bucket(cls.bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
        except Exception as e:
            print("Error deleting file: ", e)
            return False
    
    @classmethod
    def get_singed_put_url(cls, blob_name, model_name=None, instance_uid=None):
        blob_path = f"files/{blob_name}"
        if model_name:
            blob_path = f"{model_name}/{blob_name}"
        if model_name and instance_uid:
            blob_path = f"{model_name}/{instance_uid}/{blob_name}"
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(cls.bucket_name)
        blob = bucket.blob(blob_path)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=20),
            method="PUT",
            content_type="application/octet-stream",
        )
        public_url = f"https://storage.googleapis.com/{cls.bucket_name}/{blob_path}"
        return url, public_url

    @classmethod
    def upload_file(cls, url, file_bytes):
        response = requests.put(url, data=file_bytes, headers={"Content-Type": "application/octet-stream"})
        print("response.text: ", response.text)
        return response.status_code == 200

class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a media file path from MEDIA_URL
    not google generated one."""

    bucket_name = setting('GS_STATIC_BUCKET_NAME')

    def url(self, name):
        """Gives correct STATIC_URL and not google generated url."""
        return urljoin(settings.STATIC_URL, name)

