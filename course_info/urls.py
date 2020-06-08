from django.urls import path, re_path

from course_info import views


urlpatterns = [
    path('tool_config', views.tool_config, name='tool_config'),
    path('lti_launch', views.lti_launch, name='lti_launch'),
    re_path(r'^widget', views.widget, name='widget'),
]
