import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from dotenv import load_dotenv

# Load AWS credentials from .env
load_dotenv()

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION", "ap-south-1")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=region
)

def upload_file_to_s3(local_path, bucket, s3_key):
    try:
        s3_client.upload_file(local_path, bucket, s3_key)
        print(f" Uploaded: {local_path} → s3://{bucket}/{s3_key}")
        return True
    except (BotoCoreError, ClientError) as e:
        print(f" Upload failed: {e}")
        return False
