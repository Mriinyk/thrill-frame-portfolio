from django.urls import path
from . import views


app_name = "thrill_frame_app"

urlpatterns = [
    path('', views.index, name='home'),
    path('video/', views.index, name='video'),
    path('photos/', views.index, name='photos'),
    path('contacts/', views.index, name='contacts'),
]
