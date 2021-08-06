from django.forms import TextInput, EmailInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your username')
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your e-mail')
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your first name')
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your last name')
            }),
        }
        }
