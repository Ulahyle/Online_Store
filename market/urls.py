from django.urls import path, include
from rest_framework.routers import DefaultRouter
from market import views


public_router = DefaultRouter()
public_router.register(r'products', views.PublicProductViewSet, basename='public-product')
public_router.register(r'categories', views.PublicCategoryViewSet, basename='public-category')

dashboard_router = DefaultRouter()
dashboard_router.register(r'stores', views.StoreViewSet, basename='store')
dashboard_router.register(r'categories', views.CategoryViewSet, basename='category')
dashboard_router.register(r'products', views.ProductViewSet, basename='product')


urlpatterns = [
    path('dashboard/', include(dashboard_router.urls)),
    path('', include(public_router.urls)),
]
