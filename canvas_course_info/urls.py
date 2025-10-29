from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
import watchman.views
from lti_tool.views import jwks, OIDCLoginInitView
from canvas_course_info.views import config, not_authorized, ApplicationLaunchView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(".well-known/jwks.json", jwks, name="jwks"),
    path("init/<uuid:registration_uuid>/", OIDCLoginInitView.as_view(), name="init"),
    path("config/<uuid:registration_uuid>/", config, name="config"),
    path("launch/", ApplicationLaunchView.as_view(), name="launch"),
    path("not_authorized/", not_authorized, name="not_authorized"),
    path(
        "course_info/",
        include(("course_info.urls", "course_info"), namespace="course_info"),
    ),
    path("w/", include("watchman.urls")),
    re_path(r"^status/?$", watchman.views.bare_status),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [re_path(r"^__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
