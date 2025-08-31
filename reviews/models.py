from django.db import models
from django.conf import settings
from core.models import AbstractBaseModel
from market.models import Product


class Review(AbstractBaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    title = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return f"Review for {self.product.name} by {self.customer.username}"
