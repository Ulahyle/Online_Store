from django.urls import path, include
from rest_framework.routers import SimpleRouter

from store.views import (
    CustomerViewSet, StoreViewSet, CategoryViewSet, ProductViewSet, ReviewViewSet,
    CartViewSet, CartItemViewSet, OrderViewSet, OrderItemViewSet, PaymentViewSet
)


router = SimpleRouter()

router.register(r'customers', CustomerViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cartitems', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'ordersitems', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = router.urls