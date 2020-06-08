from .base import *

ALLOWED_HOSTS = ['.tlt.harvard.edu']

# SSL is terminated at the ELB so look for this header to know that we should be in ssl mode
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True

# AWS staticfiles storage
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = SECURE_SETTINGS.get('static_files_s3_bucket')
AWS_QUERYSTRING_AUTH = False
AWS_LOCATION = SECURE_SETTINGS.get('static_files_s3_prefix')
AWS_DEFAULT_ACL = None
