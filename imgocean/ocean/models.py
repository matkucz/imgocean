import os
from datetime import timedelta
from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator
)
from django.contrib.auth.models import AbstractUser

def validate_exp_after(value):
    now = timezone.now()
    min_value = now + timedelta(seconds=299)
    max_value = now + timedelta(seconds=29999)
    if not (min_value <= value <= max_value):
        raise ValidationError("Expiration seconds should be between 300 and 30000.")
    return value

def upload_to(instance, filename):
    _, extension = os.path.splitext(filename)
    return f'{uuid4()}{extension}'

class Account(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    can_generate_exp_links = models.BooleanField(
        null=False,
        default=False
    )

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.username


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    img = models.ImageField(
        max_length=50,
        upload_to=upload_to,
        validators=[
            FileExtensionValidator(
                ['jpg', 'jpeg', 'png'],
                'Allowed formats are [JPG, JPEG, PNG].'
            )
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    exp_after = models.DateTimeField(
        null=True,
        validators=[
            validate_exp_after
        ]
    )

    def __str__(self) -> str:
        return self.img.name

class Size(models.Model):
    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    height = models.PositiveIntegerField()

    class Meta:
        unique_together = [
            ['account_type', 'height']
        ]

    def __str__(self) -> str:
        return f"{self.height}"