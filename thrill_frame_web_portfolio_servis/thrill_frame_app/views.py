from django.shortcuts import render
from .models import NewRelease, VideoSlide
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserAuthForm
from django.shortcuts import render
from django.db.models import F
from .models import SiteVisit


def index(request):
    slides = VideoSlide.objects.filter(is_active=True)
    new_releases = NewRelease.objects.filter(is_active=True).order_by(
    'order', '-created_at'
    )[:3]

    visit, _ = SiteVisit.objects.get_or_create(id=1)
    SiteVisit.objects.filter(id=1).update(count=F('count') + 1)
    visit.refresh_from_db()

    context = {
        'slides': slides,
        'visits_count': visit.count,
        'new_releases': new_releases,
        #'videos_count': VideoWork.objects.count(),
        #'photos_count': PhotoSession.objects.count(),
    }

    return render(request, 'thrill_frame_app/index.html', context)


User = get_user_model()

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'index'
    
    if request.user.is_authenticated:
        return redirect(next_url)

    error_message = None

    if request.method == 'POST':
        form = UserAuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # Якщо користувач існує — перевіряємо пароль
                user_obj = User.objects.get(username=username)
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(next_url)
                else:
                    error_message = "Невірний пароль для цього користувача."
            except User.DoesNotExist:
                # Якщо користувача немає — реєструємо та входимо
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect(next_url)
    else:
        form = UserAuthForm()

    return render(request, 'thrill_frame_app/login.html', {
        'form': form,
        'next': next_url,
        'error_message': error_message
    })

def logout_view(request):
    next_url = request.GET.get('next', 'index')
    logout(request)
    return redirect(next_url)
