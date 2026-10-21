import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='myaccesskey123',
    aws_secret_access_key='mysecretkey456',
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = 'hh-lake'
FILE_NAME = 'python_vacancies.jsonl'

try:
    s3.upload_file(FILE_NAME, BUCKET_NAME, FILE_NAME)
    print("файл загружен")
except Exception as e:
    print(f"ошибка {e}")