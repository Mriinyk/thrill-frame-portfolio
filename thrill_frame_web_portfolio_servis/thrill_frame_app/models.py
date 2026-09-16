import re
from django.db import models
from django.core.exceptions import ValidationError

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
