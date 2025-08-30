from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import AbstractBaseModel


class Customer(AbstractUser, AbstractBaseModel):
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    def __str__(self):
        return self.username or self.email or str(self.id)
