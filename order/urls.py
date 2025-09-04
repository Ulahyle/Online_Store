from rest_framework.routers import DefaultRouter
from order.views import OrderViewSet


router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = router.urls
