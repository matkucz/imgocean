from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account
from .forms import CustomUserChangeForm, CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    dorm = CustomUserChangeForm
    model = User

admin.site.register(User, CustomUserAdmin)
admin.site.register(Account)