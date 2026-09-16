from django.contrib import admin
from .models import VideoSlide

@admin.register(VideoSlide)
class VideoSlideAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'youtube_id', 'is_active')
    list_display_links = ('title',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',) 
    search_fields = ('title', 'overlay_text', 'youtube_id')
