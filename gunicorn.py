# from getenv import env
# import dotenv
# dotenv.read_dotenv()
from dce_course_info.settings import aws as settings

#TODO: can we just delete this file from TLT's server? - they aren't going to use Gunicorn. 
# settings.GUNICORN_WORKERS and settings.GUNICORN_TIMEOUT seem to not work here because
# the app hasn't initialized at this point. Not liking the hard-coded stuff though.

workers = 4 #env('GUNICORN_WORKERS', 4)
timeout = 60 #env('GUNICORN_TIMEOUT', 60)
