from django.forms import ModelForm, TextInput, EmailInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome de usuário'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu e-mail'
            })
        }
