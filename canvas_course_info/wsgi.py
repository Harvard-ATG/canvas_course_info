"""
WSGI config for canvas_course_info project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
# import os
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canvas_course_info.settings.aws")
#
# from django.core.wsgi import get_wsgi_application
# from dj_static import Cling
#
# application = Cling(get_wsgi_application())

import os
from dj_static import Cling
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canvas_course_info.settings.aws")

# Need Cling() for static assets with a wsgi server
application = Cling(get_wsgi_application())