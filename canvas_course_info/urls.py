from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^course_info/', include('course_info.urls')),
)
