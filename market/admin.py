from django.contrib import admin
from market.models import Store, Category, Product, ProductImage


admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
