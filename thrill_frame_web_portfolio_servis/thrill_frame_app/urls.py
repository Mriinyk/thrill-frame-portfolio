from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "thrill_frame_app"

urlpatterns = [
    path('', views.index, name='home'),
    path('video/', views.index, name='video'),
    path('photos/', views.index, name='photos'),
    path('contacts/', views.index, name='contacts'),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='thrill_frame_app/registration/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
]
