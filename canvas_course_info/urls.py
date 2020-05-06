from django.urls import path, include

urlpatterns = [
    path('course_info/', include(('course_info.urls', 'course_info'), namespace='course_info')),
]
