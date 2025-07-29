from django.urls import path
from accounts.views import RegisterView, SendOTPView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/', SendOTPView.as_view(), name='otp'),
    path('login/', TokenObtainPairView.as_view(), name='login'),         # JWT login
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT refresh
]