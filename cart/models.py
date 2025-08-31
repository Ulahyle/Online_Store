from django.db import models
from django.conf import settings
from core.models import AbstractBaseModel
from market.models import Product


class Cart(AbstractBaseModel):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    
    def __str__(self):
        return f"Cart for {self.customer.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    # Price snapshots are not needed in the cart, as prices can change. We calculate totals dynamically.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"
