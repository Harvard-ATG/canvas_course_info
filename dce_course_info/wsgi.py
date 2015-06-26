"""
WSGI config for dce_course_info project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
# import os
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dce_course_info.settings.aws")
#
# from django.core.wsgi import get_wsgi_application
# from dj_static import Cling
#
# application = Cling(get_wsgi_application())

import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dce_course_info.settings.aws")
#application = get_wsgi_application()
from dj_static import Cling
#
application = Cling(get_wsgi_application())