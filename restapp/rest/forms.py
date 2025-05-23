from django.forms import ModelForm, ModelChoiceField
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
