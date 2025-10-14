from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'celular', 'data_nascimento', 'password1', 'password2']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'celular', 'data_nascimento']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Usuário")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)
