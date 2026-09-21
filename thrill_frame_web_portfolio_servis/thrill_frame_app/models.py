import re
import requests
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class User(AbstractUser):
    pass


def validate_youtube_input(value):
    pattern = r'(?:v=|\/embed\/|\/youtu\.be\/|\/v\/|^)([a-zA-Z0-9_-]{11})'
    if not re.search(pattern, value.strip()):
        raise ValidationError('Введіть коректний 11-значний YouTube ID або посилання на відео.')


class VideoSlide(models.Model):
    title = models.CharField("Назва (для адмінки)", max_length=150)
    youtube_id = models.CharField(
        "YouTube Video ID або Посилання", 
        max_length=255,
        validators=[validate_youtube_input],
        help_text="Підтримуються посилання youtube.com, youtu.be або чистий ID"
    )
    overlay_text = models.CharField("Текст оверлею (знизу зліва)", max_length=255)
    order = models.PositiveIntegerField("Порядок відображення", default=0)
    is_active = models.BooleanField("Активний", default=True)

    class Meta:
        verbose_name = "Відео слайд"
        verbose_name_plural = "Відео слайди"
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"

    def save(self, *args, **kwargs):
        pattern = r'(?:v=|\/embed\/|\/youtu\.be\/|\/v\/|^)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, self.youtube_id.strip())
        if match:
            self.youtube_id = match.group(1)
        super().save(*args, **kwargs)


class SiteVisit(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Відвідувань: {self.count}"


from django.db import models
import re

class VideoWork(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва")
    video_url = models.URLField(verbose_name="Посилання на відео")

    @property
    def youtube_id(self):
        match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11}).*', self.video_url)
        return match.group(1) if match else None

    @property
    def thumbnail_url(self):
        if self.youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/maxresdefault.jpg"
        return ""

    def __str__(self):
        return self.title


class PhotoSession(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва")

    def __str__(self):
        return self.title


class NewRelease(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    category = models.CharField("Категорія", max_length=100)
    video_url = models.URLField("Посилання на YouTube")
    is_active = models.BooleanField("Активно", default=True)
    order = models.PositiveIntegerField(
        "Порядок сортування",
        default=0,
        help_text="Менше число = вище у списку (0, 1, 2...)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Новинка"
        verbose_name_plural = "Новинки"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        if not self.video_url:
            return ""
        url = self.video_url.strip()
        pattern = r"(?:v=|\/embed\/|\/shorts\/|\/v\/|youtu\.be\/|\/live\/)([a-zA-Z0-9_-]{11})"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        if len(url) == 11 and re.match(r"^[a-zA-Z0-9_-]{11}$", url):
            return url
        return ""

    @property
    def thumbnail_url(self):
        if self.youtube_id:
            return (
                f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"
            )
        return ""


class ContactRequest(models.Model):
    CONTACT_CHOICES = [
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
    ]

    telegram_message_id = models.BigIntegerField(
        blank=True, 
        null=True, 
        verbose_name="ID повідомлення в Telegram"
    )

    contact_method = models.CharField(
        max_length=10, 
        choices=CONTACT_CHOICES, 
        default='telegram',
        verbose_name="Спосіб зв'язку"
    )
    social_username = models.CharField(
        max_length=100, 
        verbose_name="Нікнейм"
    )
    message = models.TextField(
        verbose_name="Повідомлення"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата створення"
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_contact_method_display()}: {self.social_username}"


# Виправлено sender=Contact на sender=ContactRequest
@receiver(pre_delete, sender=ContactRequest)
def delete_telegram_message_on_delete(sender, instance, **kwargs):
    if instance.telegram_message_id:
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '8878616904:AAGCrj25pqf0H8i-Gd_XYVNaPleLXVb6oXY')
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '610002325')

        url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
        payload = {
            'chat_id': chat_id,
            'message_id': instance.telegram_message_id
        }

        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Помилка видалення з Telegram: {e}")
