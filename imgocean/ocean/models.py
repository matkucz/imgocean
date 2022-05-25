from pydoc import describe
from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.username


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class Size(models.Model):
    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    height = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.height}"