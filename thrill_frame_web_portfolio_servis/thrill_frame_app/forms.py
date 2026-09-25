from django import forms
from django.contrib.auth.forms import UserCreationForm

from thrill_frame_app.models import (
    ContactRequest,
    PhotoComment,
    PhotoSession,
    User,
    VideoWork,
)


class UserAuthForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Створіть, або введіть існуюче ім'я користувача",
        widget=forms.TextInput(attrs={
            "class": "form-control custom-auth-input",
            "placeholder": "Ім'я користувача",
            "autocomplete": "username",
            "required": True,
        })
    )
    password = forms.CharField(
        label="Впишіть пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control custom-auth-input",
            "placeholder": "Пароль",
            "autocomplete": "current-password",
            "required": True,
        })
    )


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control custom-auth-input",
            "placeholder": "Пароль",
            "autocomplete": "new-password",
        }),
        strip=False,
    )
    password2 = forms.CharField(
        label="Підтвердіть пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control custom-auth-input",
            "placeholder": "Підтвердіть пароль",
            "autocomplete": "new-password",
        }),
        strip=False,
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
        labels = {
            "username": "Ім'я користувача",
            "password1": "Пароль",
            "password2": "Підтвердіть пароль",
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "Ім'я користувача",
                "autocomplete": "username",
            }),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ["contact_method", "social_username", "message"]
        widgets = {
            "contact_method": forms.RadioSelect(attrs={"class": "custom-radio-input"}),
            "social_username": forms.TextInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "@nickname",
                "required": True,
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "Ваше повідомлення...",
                "rows": 4,
                "required": True,
            })
        }
        labels = {
            "contact_method": "Оберіть соціальну мережу для зв'язку",
            "social_username": "Введіть нікнейм",
            "message": "Напишіть повідомлення",
        }


class VideoWorkForm(forms.ModelForm):
    class Meta:
        model = VideoWork
        fields = ["title", "video_url"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "Введіть заголовок відео",
            }),
            "video_url": forms.URLInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "https://www.youtube.com/watch?v=...",
            }),
        }


class PhotoSessionForm(forms.ModelForm):
    class Meta:
        model = PhotoSession
        fields = ["title", "cover_url", "drive_folder_url"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "Напр.: Lose Yourself",
            }),
            "cover_url": forms.URLInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "Напр.: https://images.unsplash.com...",
            }),
            "drive_folder_url": forms.URLInput(attrs={
                "class": "form-control custom-auth-input",
                "placeholder": "Напр.: https://drive.google.com/drive/folders/...",
            }),
        }


class PhotoCommentForm(forms.ModelForm):
    class Meta:
        model = PhotoComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Додати коментар...",
                }
            ),
        }
