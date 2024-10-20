from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'

class StaticFileStorage(S3Boto3Storage):
    location = 'static'

class ProtectedFileStorage(S3Boto3Storage):
    location = 'protected'