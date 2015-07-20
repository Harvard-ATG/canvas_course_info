from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^course_info/', include('course_info.urls')),
    url(r'^admin/', include(admin.site.urls))
)
