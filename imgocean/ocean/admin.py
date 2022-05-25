from django.contrib import admin
from .models import User, Account, Size

admin.site.register(Account)
admin.site.register(User)
admin.site.register(Size)