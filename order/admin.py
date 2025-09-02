from django.contrib import admin
from order.models import Order, OrderItem, Payment


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
