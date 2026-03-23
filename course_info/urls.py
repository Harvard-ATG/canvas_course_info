from django.urls import path, re_path

from course_info import views


urlpatterns = [
    path("launch/", views.ApplicationLaunchView.as_view(), name="lti_launch"),
    path("editor/", views.editor, name="editor"),
    path("deep_link_return/", views.deep_link_return, name="deep_link_return"),
    re_path(r"^widget", views.widget, name="widget"),
]
