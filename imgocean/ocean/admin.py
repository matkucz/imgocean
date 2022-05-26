from django.contrib import admin
from .models import User, Account, Size, Image

admin.site.register(Account)
admin.site.register(User)
admin.site.register(Size)
admin.site.register(Image)