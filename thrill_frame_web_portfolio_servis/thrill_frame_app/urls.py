from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import VideoListView, VideoUpdateView, VideoDeleteView

app_name = "thrill_frame_app"

urlpatterns = [
    path('', views.index, name='home'),
    path('photos/', views.index, name='photos'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('videos/', VideoListView.as_view(), name='video_page'),
    path('video/add/', views.add_video, name='add_video'),
    path('video/<int:video_id>/like/', views.toggle_like, name='toggle_like'),
    path('video/<int:video_id>/comment/', views.add_comment, name='add_comment'),
    path('video/<int:pk>/update/', VideoUpdateView.as_view(), name='video_update'),
    path('video/<int:pk>/delete/', VideoDeleteView.as_view(), name='video_delete'),
]
