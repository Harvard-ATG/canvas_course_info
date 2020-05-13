from django.conf import settings
from django.urls import include, path, re_path

import watchman.views

urlpatterns = [
    path('course_info/', include(('course_info.urls', 'course_info'), namespace='course_info')),
    path('w/', include('watchman.urls')),
    re_path(r'^status/?$', watchman.views.bare_status),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass  # This is OK for a deployed instance running in DEBUG mode
