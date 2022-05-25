from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Account

class CustomUserCreationForm(UserCreationForm):
    model = User
    fields = '__all__'

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'account_type')