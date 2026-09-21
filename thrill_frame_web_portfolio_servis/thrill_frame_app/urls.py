from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "thrill_frame_app"

urlpatterns = [
    path('', views.index, name='home'),
    path('photos/', views.index, name='photos'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('video/', views.video_page, name='video_page'),
    path('video/add/', views.add_video, name='add_video'),
]
