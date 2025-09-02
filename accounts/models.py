from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import AbstractBaseModel
from django.conf import settings


class Customer(AbstractUser, AbstractBaseModel):
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    def __str__(self):
        return self.username or self.email or str(self.id)

class Address(AbstractBaseModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=100, blank=True, null=True, help_text="E.g., Home, Work")
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, help_text="State/Province/Region")
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.username} - {self.line1}, {self.city}"
