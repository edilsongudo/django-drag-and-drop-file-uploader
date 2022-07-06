import os
import uuid

import boto3
import requests
from django.conf import settings


def handle_incoming_file_chunk(file):
    file_id = file.name
    if not os.path.isdir(settings.MEDIA_ROOT):
        os.mkdir(settings.MEDIA_ROOT)
    temporary_path = os.path.join(settings.MEDIA_ROOT, file_id)
    with open(temporary_path, 'ab') as f:
        f.write(file.read())
    return temporary_path


def handle_last_file_chunk(temporary_path, filename):
    final_filename = filename
    final_path = os.path.join(settings.MEDIA_ROOT, final_filename)
    if os.path.exists(final_path):
        final_filename = (
            os.path.splitext(filename)[0]
            + ' - '
            + uuid.uuid4().hex[0:3]
            + os.path.splitext(filename)[1]
        )
        final_path = os.path.join(settings.MEDIA_ROOT, final_filename)
    os.rename(temporary_path, final_path)
    return final_path


def generate_presigned_url(key):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=boto3.session.Config(
            signature_version=settings.AWS_S3_SIGNATURE_VERSION
        ),
    )
    client_method = 'put_object'
    method_parameters = {
        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
        'Key': key,
    }
    expires_in = 3600

    url = s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params=method_parameters,
        ExpiresIn=expires_in,
    )
    return url


def generate_aws_s3_object_url(key):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3 = boto3.resource('s3')
    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)[
        'LocationConstraint'
    ]
    url = 'https://s3-%s.amazonaws.com/%s/%s' % (location, bucket_name, key)
    return url


def milliseconds_to_hours(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = millis / (1000 * 60)
    minutes = int(minutes)
    return f'{minutes}:{seconds}'
