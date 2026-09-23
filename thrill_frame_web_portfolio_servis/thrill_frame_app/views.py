import requests
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404 ,redirect
from django.db.models import Q, F
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.models import User
from django.db.models import F
from .models import SiteVisit, VideoWork, VideoComment, PhotoSession, PhotoComment, NewRelease, VideoSlide
from django.contrib import messages
from .forms import ContactForm, VideoWorkForm, PhotoSessionForm, PhotoCommentForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator


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
    # 1. Отримуємо next з POST/GET, а якщо його немає — з HTTP_REFERER (адреси сторінки, з якої перейшли)
    next_url = request.POST.get('next') or request.GET.get('next')
    
    if not next_url:
        referer = request.META.get('HTTP_REFERER', '')
        # Перевіряємо, щоб referer був з нашого сайту і це не сама сторінка логіну
        if referer and 'login' not in referer:
            next_url = referer

    if request.method == 'POST':
        user_name = request.POST.get('username', '').strip()
        user_pass = request.POST.get('password', '').strip()

        if not user_name or not user_pass:
            messages.error(request, "Заповніть усі поля.")
            return render(request, 'thrill_frame_app/registration/login.html', {'next': next_url})

        user = authenticate(request, username=user_name, password=user_pass)

        if user is not None:
            login(request, user)
            request.session.set_expiry(1209600)
            if next_url:
                return redirect(next_url)
            return redirect('thrill_frame_app:home')
        else:
            if User.objects.filter(username=user_name).exists():
                messages.error(request, "Користувач з таким ім'ям існує, але пароль невірний.")
            else:
                try:
                    User.objects.create_user(username=user_name, password=user_pass)
                    new_user = authenticate(request, username=user_name, password=user_pass)
                    if new_user is not None:
                        login(request, new_user)
                        request.session.set_expiry(1209600)
                        if next_url:
                            return redirect(next_url)
                        return redirect('thrill_frame_app:home')
                except Exception as e:
                    messages.error(request, f"Помилка створення: {e}")

    return render(request, 'thrill_frame_app/registration/login.html', {'next': next_url})


def logout_view(request):
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    logout(request)
    
    # Запобігаємо зацикленню, якщо next вказує на сторінку входу чи виходу
    if 'login' in next_url or 'logout' in next_url:
        return redirect('thrill_frame_app:home')
        
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


def add_video(request):
    if not request.user.is_superuser:
        return redirect('thrill_frame_app:video_page')
        
    if request.method == 'POST':
        form = VideoWorkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thrill_frame_app:video_page')
    else:
        form = VideoWorkForm()
        
    return render(request, 'thrill_frame_app/add_video.html', {'form': form})


@login_required
def toggle_like(request, video_id):
    if request.method == "POST":
        video = get_object_or_404(VideoWork, id=video_id)
        if video.likes.filter(id=request.user.id).exists():
            video.likes.remove(request.user)
            liked = False
        else:
            video.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'total_likes': video.total_likes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_comment(request, video_id):
    if request.method == "POST":
        video = get_object_or_404(VideoWork, id=video_id)
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if text:
            parent_comment = VideoComment.objects.get(id=parent_id) if parent_id else None
            comment = VideoComment.objects.create(
                video=video,
                user=request.user,
                parent=parent_comment,
                text=text
            )
            return JsonResponse({
                'status': 'success',
                'username': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                'comment_id': comment.id,
                'parent_id': parent_id
            })
    return JsonResponse({'error': 'Invalid text'}, status=400)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class VideoUpdateView(AdminRequiredMixin, UpdateView):
    model = VideoWork
    fields = ['title', 'video_url']
    template_name = 'thrill_frame_app/video_form.html'
    
    def get_success_url(self):
        return f"{reverse('thrill_frame_app:video_page')}#video-{self.object.id}"


class VideoDeleteView(AdminRequiredMixin, DeleteView):
    model = VideoWork
    template_name = 'thrill_frame_app/video_confirm_delete.html'
    success_url = reverse_lazy('thrill_frame_app:video_page')


class VideoListView(ListView):
    model = VideoWork
    template_name = "thrill_frame_app/videos.html"
    context_object_name = "videos"
    paginate_by = 5

    def get_queryset(self):
        queryset = VideoWork.objects.all().order_by("-created_at", "-id")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(title__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context


def photos_list(request):
    query = request.GET.get('q', '')
    if query:
        photos = PhotoSession.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        photos = PhotoSession.objects.all().order_by('-created_at')

    paginator = Paginator(photos, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'thrill_frame_app/photos.html', {
        'photoshoots': page_obj.object_list,
        'page_obj': page_obj,
        'search_query': query,
        'is_paginated': page_obj.has_other_pages(),
        'comment_form': PhotoCommentForm()
    })

@login_required
def photo_create(request):
    if not request.user.is_superuser:
        return redirect('thrill_frame_app:photos_list')
    if request.method == 'POST':
        form = PhotoSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thrill_frame_app:photos_list')
    else:
        form = PhotoSessionForm()
    return render(request, 'thrill_frame_app/photo_form.html', {'form': form, 'title': 'Додати фотосесію'})

@login_required
def photo_update(request, pk):
    if not request.user.is_superuser:
        return redirect('thrill_frame_app:photos_list')
    photo = get_object_or_404(PhotoSession, pk=pk)
    if request.method == 'POST':
        form = PhotoSessionForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            return redirect('thrill_frame_app:photos_list')
    else:
        form = PhotoSessionForm(instance=photo)
    return render(request, 'thrill_frame_app/photo_form.html', {'form': form, 'title': 'Оновити фотосесію'})

@login_required
def photo_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('thrill_frame_app:photos_list')
    photo = get_object_or_404(PhotoSession, pk=pk)
    if request.method == 'POST':
        photo.delete()
        return redirect('thrill_frame_app:photos_list')
    return render(request, 'thrill_frame_app/photo_confirm_delete.html', {'photo': photo})

@login_required
def photo_like(request, pk):
    photo = get_object_or_404(PhotoSession, pk=pk)
    if photo.likes.filter(id=request.user.id).exists():
        photo.likes.remove(request.user)
        liked = False
    else:
        photo.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': photo.likes.count()})

@login_required
def photo_comment(request, pk):
    photo = get_object_or_404(PhotoSession, pk=pk)
    if request.method == 'POST':
        form = PhotoCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.photo_session = photo
            comment.user = request.user
            comment.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'username': comment.user.username,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                    'comment_count': photo.comments.count(),
                })
    return redirect('thrill_frame_app:photos_list')
