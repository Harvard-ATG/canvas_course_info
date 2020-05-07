from django.conf import settings
from django.urls import path, re_path, include

urlpatterns = [
    path('course_info/', include(('course_info.urls', 'course_info'), namespace='course_info')),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass  # This is OK for a deployed instance running in DEBUG mode
