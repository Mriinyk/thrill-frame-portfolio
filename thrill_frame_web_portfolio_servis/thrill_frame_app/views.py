import requests
from django.conf import settings
from django.shortcuts import render
from .models import NewRelease, VideoSlide
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserAuthForm
from django.shortcuts import render
from django.db.models import F
from .models import SiteVisit, VideoWork, PhotoSession
from django.contrib import messages
from .forms import ContactForm


def index(request):
    slides = VideoSlide.objects.filter(is_active=True)
    new_releases = NewRelease.objects.filter(is_active=True).order_by(
        'order', '-created_at'
    )[:3]

    # Інкремент лічильника при відвідуванні головної сторінки
    SiteVisit.objects.get_or_create(id=1)
    SiteVisit.objects.filter(id=1).update(count=F('count') + 1)

    context = {
        'slides': slides,
        'new_releases': new_releases,
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


def send_telegram_notification(contact_instance):
    """
    Надсилає сповіщення в Telegram та зберігає message_id для подальшого видалення.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '8878616904:AAGCrj25pqf0H8i-Gd_XYVNaPleLXVb6oXY')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '610002325')

    contact_method = contact_instance.contact_method
    social_username = contact_instance.social_username
    user_message = contact_instance.message

    if contact_method == 'telegram':
        link = f"https://t.me/{social_username.replace('@', '')}"
    else:
        link = f"https://instagram.com/{social_username.replace('@', '')}"

    text = (
        f"🔥 <b>Нова заявка з сайту! (#ID: {contact_instance.id})</b>\n\n"
        f"<b>Зв'язок:</b> {contact_instance.get_contact_method_display()}\n"
        f"<b>Нік:</b> {social_username}\n"
        f"<b>Посилання:</b> <a href='{link}'>Перейти до профілю</a>\n\n"
        f"<b>Повідомлення:</b>\n<i>{user_message}</i>"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('result', {}).get('message_id')
            if message_id:
                contact_instance.telegram_message_id = message_id
                contact_instance.save(update_fields=['telegram_message_id'])
            return True
    except Exception as e:
        print(f"Помилка відправки Telegram сповіщення: {e}")
    
    return False


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_request = form.save()

            # Надсилаємо сповіщення та фіксуємо telegram_message_id
            send_telegram_notification(contact_request)

            messages.success(request, "Ваше повідомлення успішно надіслано!")
            return redirect('thrill_frame_app:contact')
    else:
        form = ContactForm()

    return render(request, 'thrill_frame_app/contact.html', {'form': form})
