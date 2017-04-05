from django.conf.urls import url

from course_info import views


urlpatterns = [
    url(r'^tool_config$', views.tool_config, name='tool_config'),
    url(r'^lti_launch$', views.lti_launch, name='lti_launch'),
    url(r'^widget', views.widget, name='widget'),
]
