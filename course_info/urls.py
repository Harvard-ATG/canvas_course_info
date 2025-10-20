from django.urls import path
from . import views

app_name = "course_info"

urlpatterns = [
    path("config/<uuid:registration_uuid>/", views.config, name="config"),
    path("launch/", views.ApplicationLaunchView.as_view(), name="launch"),
    path("not_authorized/", views.not_authorized, name="not_authorized"),
    path("widget/", views.widget, name="widget"),
    path("editor/", views.editor, name="editor"),
]
