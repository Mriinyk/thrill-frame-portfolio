from django.shortcuts import render
from .models import NewRelease, VideoSlide
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserAuthForm
from django.shortcuts import render
from django.db.models import F
from .models import SiteVisit
from django.contrib import messages
import requests
from .forms import ContactForm


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


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_request = form.save()

            contact_method = contact_request.contact_method
            social_username = contact_request.social_username
            user_message = contact_request.message

            BOT_TOKEN = '8878616904:AAGCrj25pqf0H8i-Gd_XYVNaPleLXVb6oXY'
            CHAT_ID = '610002325'

            if contact_method == 'telegram':
                link = f"https://t.me/{social_username.replace('@', '')}"
            else:
                link = f"https://instagram.com/{social_username.replace('@', '')}"

            text = (
                f"🔥 <b>Нова заявка з сайту! (#ID: {contact_request.id})</b>\n\n"
                f"<b>Зв'язок:</b> {contact_request.get_contact_method_display()}\n"
                f"<b>Нік:</b> {social_username}\n"
                f"<b>Посилання:</b> <a href='{link}'>Перейти до профілю</a>\n\n"
                f"<b>Повідомлення:</b>\n<i>{user_message}</i>"
            )

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': CHAT_ID,
                'text': text,
                'parse_mode': 'HTML'
            }

            try:
                requests.post(url, data=payload)
                messages.success(request, "Ваше повідомлення успішно надіслано!")
            except Exception:
                messages.success(request, "Ваше повідомлення успішно збережено!")

            return redirect('thrill_frame_app:contact')
    else:
        form = ContactForm()

    return render(request, 'thrill_frame_app/contact.html', {'form': form})
