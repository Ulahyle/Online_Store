from django.urls import path, include
from rest_framework.routers import DefaultRouter
from market import views


router = DefaultRouter()
# seller dashboard urls
router.register(r'stores', views.StoreViewSet, basename='store')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('dashboard/', include(router.urls)),
]