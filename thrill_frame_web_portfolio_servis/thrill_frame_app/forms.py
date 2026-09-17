from django import forms

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
