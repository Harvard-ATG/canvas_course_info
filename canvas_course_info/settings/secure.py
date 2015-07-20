SECURE_SETTINGS = {
    'enable_debug' : False,
    'offer_text': True,

    'django_secret_key': 'FW3*cqFmwZM#MY7VapW_gqk3?Mx5s2emMC&@z?YP',

    'db_default_name': 'canvas_course_info',
    'db_default_user': 'canvas_course_info',
    'db_default_password': 'password',
    'db_default_host': '127.0.0.1',
    'db_default_port': 5432,

    #'redis_url': '127.0.0.1:6379',

    #'lti_oauth_course_info_consumer_key': 'your_key',
    #'lti_oauth_course_info_consumer_secret': 'your_secret',
    'lti_oath_credentials': {'consumer_key': 'your_key', 'consumer_secret': 'your_secret'},

    'icommons_api_token': 'c308548ffe204cab945a077cca94cc3f21f1dee8',
    'icommons_base_url': 'https://icommons.harvard.edu',

    'course_instance_id': '312976',

    #doesn't work yet
    'gunicorn_workers': 4,
    'gunicorn_timeout': 60,
}