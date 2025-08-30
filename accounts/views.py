import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django_redis import get_redis_connection

from accounts.models import Customer
from accounts.serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    OTPLoginRequestSerializer
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp = str(random.randint(100000, 999999))
            phone = serializer.validated_data.get('phone_number')
            email = serializer.validated_data.get('email')
            identifier = phone or email
            key = f"otp:{identifier}"

            redis_conn = get_redis_connection("default")
            redis_conn.setex(key, 360, otp)

            print(f"OTP for {identifier}: {otp}")
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone_number")
        email = serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")

        identifier = phone or email
        key = f"otp:{identifier}"

        redis_conn = get_redis_connection("default")
        stored_otp = redis_conn.get(key)

        if stored_otp is None:
            return Response({"detail": "OTP expired or does not exist"}, status=400)

        if stored_otp.decode() != otp:
            return Response({"detail": "Incorrect OTP"}, status=400)

        redis_conn.delete(key)

        user, _ = Customer.objects.get_or_create(
            phone_number=phone,
            defaults={'email': email} if email else {}
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "email": user.email
            }
        })
    

class OTPLoginRequestView(APIView):
    def post(self, request):
        serializer = OTPLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone_number")
        email = serializer.validated_data.get("email")
        identifier = phone or email

        otp = str(random.randint(1000000, 9999999))
        key = f"otp:{identifier}"

        redis_conn = get_redis_connection("default")
        redis_conn.setex(key, 360, otp)

        print(f"OTP for {identifier}: {otp}")
        return Response({"detail": "Code sent!"}, status=200)
