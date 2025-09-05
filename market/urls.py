from django.urls import path, include
from market import views
from reviews.views import ReviewViewSet
from rest_framework_nested import routers
# from rest_framework.routers import DefaultRouter


public_router = routers.DefaultRouter()
public_router.register(r'products', views.PublicProductViewSet, basename='public-product')
public_router.register(r'categories', views.PublicCategoryViewSet, basename='public-category')

products_router = routers.NestedDefaultRouter(public_router, r'products', lookup='product')
products_router.register(r'reviews', ReviewViewSet, basename='product-reviews')

dashboard_router = routers.DefaultRouter()
dashboard_router.register(r'stores', views.StoreViewSet, basename='store')
dashboard_router.register(r'categories', views.CategoryViewSet, basename='category')
dashboard_router.register(r'products', views.ProductViewSet, basename='product')


urlpatterns = [
    path('dashboard/', include(dashboard_router.urls)),

    path('', include(public_router.urls)),
    path('', include(products_router.urls)),
]

