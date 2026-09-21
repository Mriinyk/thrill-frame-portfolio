from django import forms
from .models import ContactRequest, VideoWork


class UserAuthForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Створіть, або введіть існуюче ім'я користувача",
        widget=forms.TextInput(attrs={
            'class': 'form-control custom-auth-input',
            'placeholder': 'Ім\'я користувача',
            'autocomplete': 'username',
            'required': True
        })
    )
    password = forms.CharField(
        label="Впишіть пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control custom-auth-input',
            'placeholder': 'Пароль',
            'autocomplete': 'current-password',
            'required': True
        })
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['contact_method', 'social_username', 'message']
        widgets = {
            'contact_method': forms.RadioSelect(attrs={'class': 'custom-radio-input'}),
            'social_username': forms.TextInput(attrs={
                'class': 'form-control custom-auth-input',
                'placeholder': '@nickname',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control custom-auth-input',
                'placeholder': 'Ваше повідомлення...',
                'rows': 4,
                'required': True
            })
        }
        labels = {
            'contact_method': "Оберіть соціальну мережу для зв'язку",
            'social_username': "Введіть нікнейм",
            'message': "Напишіть повідомлення"
        }


class VideoWorkForm(forms.ModelForm):
    class Meta:
        model = VideoWork
        fields = ['title', 'video_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control custom-auth-input', 
                'placeholder': 'Введіть заголовок відео'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control custom-auth-input', 
                'placeholder': '[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)...'
            }),
        }
