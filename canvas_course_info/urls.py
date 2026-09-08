from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

import watchman.views
from lti_tool.views import jwks, OIDCLoginInitView

from canvas_course_info.views import ConfigView

urlpatterns = [
    path(
        "course_info/",
        include(("course_info.urls", "course_info"), namespace="course_info"),
    ),
    path("config/", ConfigView.as_view(), name="config"),
    path(".well-known/jwks.json", jwks, name="jwks"),
    path("init/<uuid:registration_uuid>/", OIDCLoginInitView.as_view(), name="init"),
    path("admin/", admin.site.urls),
    path("w/", include("watchman.urls")),
    re_path(r"^status/?$", watchman.views.bare_status),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [
            re_path(r"^__debug__/", include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass  # This is OK for a deployed instance running in DEBUG mode
