from django.contrib import admin
from .models import NewRelease, VideoSlide, ContactRequest

@admin.register(VideoSlide)
class VideoSlideAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'youtube_id', 'is_active')
    list_display_links = ('title',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',) 
    search_fields = ('title', 'overlay_text', 'youtube_id')


@admin.register(NewRelease)
class NewReleaseAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'category', 'is_active', 'created_at')
    list_display_links = ('title',)
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'category')
    ordering = ('order', '-created_at')


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_method', 'social_username', 'created_at')
    list_filter = ('contact_method', 'created_at')
    search_fields = ('social_username', 'message')
    readonly_fields = ('created_at',)
