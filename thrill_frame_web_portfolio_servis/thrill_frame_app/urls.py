from django.urls import path
from .views import index


app_name = "thrill_frame_app"

urlpatterns = [
    path("", index, name="index")
]
