from django.conf.urls import include, url

urlpatterns = [
    url(r'^course_info/', include('course_info.urls')),
]
