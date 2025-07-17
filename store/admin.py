from django.contrib import admin

from store.models import (
    Customer, Store, Category, Product, Review,
    Cart, CartItem, Order, OrderItem, Payment
)


admin.site.register(Customer)
admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)