import boto3
import os
from dotenv import load_dotenv
load_dotenv()

class StorageManager:
    def __init__(self):
        self.bucket_name = 'habiteer'
        self.s3_client = boto3.client(
            's3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name='ru-central1'
        )

    def list_images(self, prefix=''):
        """
        List all image files (JPEG/PNG) in the bucket under a given prefix.
        :param prefix: Folder path or prefix to filter objects.
        :return: List of image file names.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [
                    obj['Key'] for obj in response['Contents']
                    if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png'))
                ]
            else:
                return []
        except Exception as e:
            print(f"Error listing images: {e}")
            return []
        
    def list_gif_images(self, prefix=''):
        """
        List all gif image files in the bucket under a given prefix.
        :param prefix: Folder path or prefix to filter objects.
        :return: List of gif image file names.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [
                    obj['Key'] for obj in response['Contents']
                    if obj['Key'].lower().endswith('.gif')
                ]
            else:
                return []
        except Exception as e:
            print(f"Error listing gif images: {e}")
            return []
        
    def get_image_url(self, image_key, expiration=3600):
        """
        Generate a pre-signed URL to access an image stored in the S3 bucket.
        :param image_key: The key (path) of the image in the bucket.
        :param expiration: The expiration time in seconds for the URL (default 1 hour).
        :return: Pre-signed URL.
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': image_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Error generating URL: {e}")
            return None

if __name__=="__main__":
    storage_manager = StorageManager()
    praises = storage_manager.list_gif_images('praises/')
    from random import choice
    print(storage_manager.get_image_url(choice(praises)) if praises else "No praises found.")