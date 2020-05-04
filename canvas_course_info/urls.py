from django.urls import path, re_path, include

urlpatterns = [
    url(r'^course_info/', include('course_info.urls')),
]
