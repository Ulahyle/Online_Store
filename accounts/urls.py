from django.urls import path, include
from accounts.views import (
    RegisterView,
    SendOTPView,
    VerifyOTPView,
    OTPLoginRequestView,
    CustomerProfileView,
    AddressViewSet
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/', SendOTPView.as_view(), name='otp'),
    path('verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', OTPLoginRequestView.as_view(), name='login'),
    path('profile/', CustomerProfileView.as_view(), name='customer-profile'),

    path('jwt_login/', TokenObtainPairView.as_view(), name='jwt_login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('', include(router.urls)),
]
