from django.urls import path, include
from rest_framework.routers import SimpleRouter
from store.views import ProductViewSet, CustomerViewSet


router = SimpleRouter()
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls))
]