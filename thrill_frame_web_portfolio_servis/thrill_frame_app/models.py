import json
import re
import requests
from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class User(AbstractUser):
    pass


def validate_youtube_input(value):
    value = value.strip()
    id_pattern = r"[a-zA-Z0-9_-]{11}"
    url_pattern = (
        r"(?:v=|youtu\.be/|youtube\.com/(?:embed/|v/|shorts/|live/))"
        rf"({id_pattern})(?:[?&#/]|$)"
    )
    if not re.fullmatch(id_pattern, value) and not re.search(url_pattern, value):
        raise ValidationError(
            "Введіть коректний 11-значний YouTube ID або посилання на відео."
        )


class VideoSlide(models.Model):
    title = models.CharField("Назва (для адмінки)", max_length=150)
    youtube_id = models.CharField(
        "YouTube Video ID або Посилання",
        max_length=255,
        validators=[validate_youtube_input],
        help_text="Підтримуються посилання youtube.com, youtu.be або чистий ID",
    )
    overlay_text = models.CharField("Текст оверлею (знизу зліва)", max_length=255)
    order = models.PositiveIntegerField("Порядок відображення", default=0)
    is_active = models.BooleanField("Активний", default=True)

    class Meta:
        verbose_name = "Відео слайд"
        verbose_name_plural = "Відео слайди"
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title}"

    def save(self, *args, **kwargs):
        value = self.youtube_id.strip()
        pattern = (
            r"(?:v=|youtu\.be/|youtube\.com/(?:embed/|v/|shorts/|live/))"
            r"([a-zA-Z0-9_-]{11})(?:[?&#/]|$)"
        )
        match = re.fullmatch(r"[a-zA-Z0-9_-]{11}", value) or re.search(
            pattern, value
        )
        if match:
            self.youtube_id = match.group(1)
        super().save(*args, **kwargs)


class SiteVisit(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Відвідувань: {self.count}"


class VideoWork(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва")
    video_url = models.URLField(verbose_name="Посилання на відео")
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_videos",
        blank=True,
        verbose_name="Вподобання",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата створення"
    )

    class Meta:
        verbose_name = "Відеоробота"
        verbose_name_plural = "Відеороботи"
        ordering = ["-created_at", "-id"]

    @property
    def youtube_id(self):
        match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11}).*", self.video_url)
        return match.group(1) if match else None

    @property
    def thumbnail_url(self):
        if self.youtube_id:
            return (
                f"https://img.youtube.com/vi/{self.youtube_id}/maxresdefault.jpg"
            )
        return ""

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class VideoComment(models.Model):
    video = models.ForeignKey(
        VideoWork,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Відео",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Батьківський коментар",
    )
    text = models.TextField(verbose_name="Текст коментаря")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Відео - коментар"
        verbose_name_plural = "Відео - коментарі"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"


class PhotoSession(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва")
    cover_url = models.URLField(
        verbose_name="Посилання на обкладинку",
        blank=True,
        null=True
    )
    drive_folder_url = models.URLField(verbose_name="Посилання на папку Google Drive")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    likes = models.ManyToManyField(User, related_name="liked_photos", blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.cover_url:
            self.cover_url = self.normalize_google_drive_url(self.cover_url)
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_google_drive_url(url):
        if not url:
            return url

        cleaned = url.strip()
        if "lh3.googleusercontent.com" in cleaned:
            return cleaned

        match = re.search(r"/d/([A-Za-z0-9_-]+)", cleaned)
        if match:
            return f"https://lh3.googleusercontent.com/d/{match.group(1)}"

        match = re.search(r"/file/d/([A-Za-z0-9_-]+)", cleaned)
        if match:
            return f"https://lh3.googleusercontent.com/d/{match.group(1)}"

        match = re.search(r"[?&]id=([A-Za-z0-9_-]+)", cleaned)
        if match:
            return f"https://lh3.googleusercontent.com/d/{match.group(1)}"

        return cleaned

    @property
    def direct_cover_url(self):
        if not self.cover_url:
            return ""
        return self.normalize_google_drive_url(self.cover_url)

    @property
    def cover_image(self):
        return self.direct_cover_url

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def gallery_images(self):
        images = []
        if self.direct_cover_url:
            images.append(self.direct_cover_url)

        folder_id = self.get_drive_folder_id()
        if not folder_id:
            return images

        cache_key = f"photo-session-gallery:{folder_id}"
        cached_files = cache.get(cache_key)
        if cached_files is not None:
            return images + [
                f"https://lh3.googleusercontent.com/d/{file_id}"
                for file_id in cached_files
                if file_id != self._cover_file_id
            ]

        try:
            response = requests.get(
                f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing",
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            return images

        files = []
        rows = re.findall(
            r"<tr\b[^>]*data-selectable[^>]*>.*?</tr>",
            response.text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for row in rows:
            file_id_match = re.search(
                r"<tr data-selectable data-id=\"([A-Za-z0-9_-]+)\"", row
            )
            image_match = re.search(
                r"data-tooltip=\"[^\"]+\.(?:jpe?g|png|webp|gif) Image\"",
                row,
                flags=re.IGNORECASE,
            )
            if file_id_match and image_match:
                files.append(file_id_match.group(1))
        cover_id = self._cover_file_id

        cache.set(cache_key, files, 60 * 60)

        for file_id in files:
            if file_id == cover_id:
                continue
            images.append(f"https://lh3.googleusercontent.com/d/{file_id}")

        return images

    @property
    def _cover_file_id(self):
        cover_id_match = re.search(
            r"(?:/d/|[?&]id=)([A-Za-z0-9_-]+)", self.cover_url or ""
        )
        return cover_id_match.group(1) if cover_id_match else None

    @property
    def gallery_images_json(self):
        return json.dumps(self.gallery_images)

    def get_drive_folder_id(self):
        match = re.search(r"folders/([a-zA-Z0-9_-]+)", self.drive_folder_url)
        if not match:
            match = re.search(r"id=([a-zA-Z0-9_-]+)", self.drive_folder_url)
        return match.group(1) if match else None

class PhotoComment(models.Model):
    photo_session = models.ForeignKey(
        PhotoSession,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Фото сесія",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Фото - коментар"
        verbose_name_plural = "Фото - коментарі"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.photo_session.title}"


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
            return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"
        return ""


class ContactRequest(models.Model):
    CONTACT_CHOICES = [
        ("telegram", "Telegram"),
        ("instagram", "Instagram"),
    ]

    telegram_message_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="ID повідомлення в Telegram",
    )

    contact_method = models.CharField(
        max_length=10,
        choices=CONTACT_CHOICES,
        default="telegram",
        verbose_name="Спосіб зв'язку",
    )
    social_username = models.CharField(
        max_length=100,
        verbose_name="Нікнейм",
    )
    message = models.TextField(
        verbose_name="Повідомлення",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення",
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_contact_method_display()}: {self.social_username}"


@receiver(pre_delete, sender=ContactRequest)
def delete_telegram_message_on_delete(sender, instance, **kwargs):
    if instance.telegram_message_id:
        bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")

        url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
        payload = {
            "chat_id": chat_id,
            "message_id": instance.telegram_message_id,
        }

        try:
            requests.post(url, json=payload, timeout=5)
        except requests.RequestException as error:
            print(f"Помилка видалення з Telegram: {error}")
