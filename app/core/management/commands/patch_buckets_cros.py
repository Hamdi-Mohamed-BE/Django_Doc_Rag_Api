from django.core.management.base import BaseCommand
from google.cloud import storage

from settings import GS_MEDIA_BUCKET_NAME, GS_STATIC_BUCKET_NAME

import os

# run echo GOOGLE_APPLICATION_CREDENTIALS
# to check if the environment variable is set
print("GOOGLE_APPLICATION_CREDENTIALS: ", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))


def set_bucket_cors(bucket_name):
    """Set CORS policy for a Google Cloud Storage bucket"""
    client = storage.Client()
    
    bucket = client.get_bucket(bucket_name)
    
    cors_policy = [
        {
            "origin": ["*"],
            "method": ["GET", "HEAD", "POST", "PUT", "DELETE"],
            "responseHeader": ["*"],
        }
    ]
    
    bucket.cors = cors_policy
    bucket.patch()
    
    print(f"CORS policy set for {bucket_name}")


class Command(BaseCommand):
    help = 'Patch the CORS settings for the buckets'

    def handle(self, *args, **kwargs):

        print("Patching CORS settings for the buckets")
        set_bucket_cors(GS_MEDIA_BUCKET_NAME)
        set_bucket_cors(GS_STATIC_BUCKET_NAME)
    

# to run this comaand use this command: python manage.py patch_buckets_cros