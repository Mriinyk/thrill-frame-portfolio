from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import NewRelease, VideoSlide, ContactRequest, VideoComment, PhotoComment

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
    list_display = ('id', 'contact_method', 'social_username', 'created_at', 'telegram_message_id')
    list_filter = ('contact_method', 'created_at')
    search_fields = ('social_username', 'message')
    readonly_fields = ('created_at', 'telegram_message_id')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'text', 'created_at', 'parent')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username')
    raw_id_fields = ('user', 'video', 'parent')


@admin.register(PhotoComment)
class PhotoCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo_session', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'photo_session__title')
    raw_id_fields = ('user', 'photo_session')


User = get_user_model()

# Безпечно перезапускаємо реєстрацію User для відображення в панелі
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
