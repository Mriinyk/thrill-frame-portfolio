from django.shortcuts import render
from .models import VideoSlide

def index(request):
    slides = VideoSlide.objects.filter(is_active=True)
    return render(request, 'thrill_frame_app/index.html', {'slides': slides})
