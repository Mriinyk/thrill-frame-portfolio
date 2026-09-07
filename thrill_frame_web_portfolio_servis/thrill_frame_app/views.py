from django.shortcuts import render

def index(request):
    return render(request, "thrill_frame_app/index.html")
