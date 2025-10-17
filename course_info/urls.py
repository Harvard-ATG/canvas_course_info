from django.urls import path, re_path
from course_info import views

app_name = "course_info"

# urlpatterns = [
#     path('tool_config', views.tool_config, name='tool_config'),
#     path('lti_launch', views.lti_launch, name='lti_launch'),
#     re_path(r'^widget', views.widget, name='widget'),
# ]

urlpatterns = [
    path(
        "config/<uuid:tool_uuid>/", views.ToolConfigView.as_view(), name="tool_config"
    ),
    path("launch/", views.CourseInfoLaunchView.as_view(), name="lti_launch"),
    path("not_authorized/", views.not_authorized, name="not_authorized"),
    re_path(r"^widget", views.widget, name="widget"),
]
