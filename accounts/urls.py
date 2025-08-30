from django.urls import path
from accounts.views import RegisterView, SendOTPView, VerifyOTPView, OTPLoginRequestView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/', SendOTPView.as_view(), name='otp'),
    path('verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', OTPLoginRequestView.as_view(), name='login'),

    path('jwt_login/', TokenObtainPairView.as_view(), name='jwt_login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
