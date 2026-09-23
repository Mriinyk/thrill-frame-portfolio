from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import VideoListView, VideoUpdateView, VideoDeleteView

app_name = "thrill_frame_app"

urlpatterns = [
    path('', views.index, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('videos/', VideoListView.as_view(), name='video_page'),
    path('video/add/', views.add_video, name='add_video'),
    path('video/<int:video_id>/like/', views.toggle_like, name='toggle_like'),
    path('video/<int:video_id>/comment/', views.add_comment, name='add_comment'),
    path('video/<int:pk>/update/', VideoUpdateView.as_view(), name='video_update'),
    path('video/<int:pk>/delete/', VideoDeleteView.as_view(), name='video_delete'),
    path('photos/', views.photos_list, name='photos_list'),
    path('photos/add/', views.photo_create, name='photo_create'),
    path('photos/<int:pk>/edit/', views.photo_update, name='photo_update'),
    path('photos/<int:pk>/delete/', views.photo_delete, name='photo_delete'),
    path('photos/<int:pk>/like/', views.photo_like, name='photo_like'),
    path('photos/<int:pk>/comment/', views.photo_comment, name='photo_comment'),
]
