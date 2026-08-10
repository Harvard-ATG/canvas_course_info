from .base import *

ALLOWED_HOSTS = [".tlt.harvard.edu"]

# SSL is terminated at the ELB so look for this header to know that we should be in ssl mode
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True

# AWS staticfiles storage - config for Django < 4.2
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_STORAGE_BUCKET_NAME = SECURE_SETTINGS.get("static_files_s3_bucket")
AWS_QUERYSTRING_AUTH = False
AWS_LOCATION = SECURE_SETTINGS.get("static_files_s3_prefix")
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = "static.tlt.harvard.edu"


# s3_bucket = SECURE_SETTINGS.get("static_files_s3_bucket")
# s3_prefix = SECURE_SETTINGS.get("static_files_s3_prefix")

# STORAGES = {
#     "staticfiles": {
#         "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
#         "OPTIONS": {
#             "bucket_name": s3_bucket,
#             "querystring_auth": False,
#             "location": s3_prefix,
#             "custom_domain": "static.tlt.harvard.edu",
#             "default_acl": None,
#         },
#     },
# }
