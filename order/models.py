from django.db import models
from django.conf import settings
from core.models import AbstractBaseModel
from accounts.models import Address
from market.models import Product


class Order(AbstractBaseModel):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # PROTECT so we can't delete a sold product
    quantity = models.PositiveIntegerField()
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at the time of order")
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name} for order {self.order.order_number}"

class Payment(AbstractBaseModel):
    class PaymentStatus(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        AUTHORIZED = 'authorized', 'Authorized'
        CAPTURED = 'captured', 'Captured'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=100) # e.g., 'Stripe', 'PayPal'
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment for {self.order.order_number} - {self.status}"
