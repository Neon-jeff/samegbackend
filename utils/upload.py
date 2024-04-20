import boto3
import environ
from botocore.exceptions import ClientError
from botocore.config import Config
from pathlib import Path

base_dir=Path(__file__).parents[1]

env=environ.Env()
environ.Env().read_env()

# initialize b2 resource object for upload operation
b2 = boto3.resource(service_name='s3',
                        endpoint_url=env('ENDPOINT'),                # Backblaze endpoint
                        aws_access_key_id=env('KEY_ID'),              # Backblaze keyID
                        aws_secret_access_key=env('BACKBLAZE_APPKEY'), # Backblaze applicationKey
                        config = Config(
                            signature_version='s3v4',
                    ))



# def upload_file( file:str, b2):
#     file_path = f'{base_dir}/static/{file}'
#     remote_path = file
#     try:
#         response = b2.Bucket(env('BUCKET')).upload_file(file_path, remote_path)
#         print(b2)
#     except ClientError as ce:
#         print('error', ce)
#     object_link=f'https://Samegproperties.s3.us-east-005.backblazeb2.com/uploads/{file}'
#     return response

def upload_image(file_path,file_name):
    b2.Bucket(env('BUCKET')).upload_file(file_path,f'property-images/{file_name}')
    object_link=f'https://Samegproperties.s3.us-east-005.backblazeb2.com/property-images/{file_name}'
    return object_link

def upload_document(file_path,file_name):
    b2.Bucket(env('BUCKET')).upload_file(file_path,f'property-documents/{file_name}')
    object_link=f'https://Samegproperties.s3.us-east-005.backblazeb2.com/property-documents/{file_name}'
    return object_link


def upload_user_property_image(file_path,file_name):
    b2.Bucket(env('BUCKET')).upload_file(file_path,f'user-property-images/{file_name}')
    object_link=f'https://Samegproperties.s3.us-east-005.backblazeb2.com/user-property-images/{file_name}'
    return object_link

