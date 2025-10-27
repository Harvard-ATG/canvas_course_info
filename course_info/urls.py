from django.urls import path
import course_info.views as views

app_name = "course_info"

urlpatterns = [
    path("widget/", views.widget, name="widget"),
]
