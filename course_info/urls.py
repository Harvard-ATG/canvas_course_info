from django.conf.urls import patterns, url

urlpatterns = patterns('course_info.views',
    url(r'^tool_config$', 'tool_config',    name = 'tool_config'),
    url(r'^lti_launch$',  'lti_launch',     name = 'lti_launch'),
    url(r'^widget',       'widget',         name = 'widget'),
)
