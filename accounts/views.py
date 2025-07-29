import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import RegisterSerializer, SendOTPSerializer, VerifyOTPSerializer
from django_redis import get_redis_connection
from utils.redis_cli import redis_client


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            key = None
            otp = str(random.randint(1000000, 9999999))

            if 'phone_number' in serializer.validated_data:
                key = f"otp_phone_{serializer.validated_data['phone_number']}!"
            elif 'email' in serializer.validated_data:
                key = f"otp_email_{serializer.validated_data['email']}!"

            redis_client.setex(key, 360, otp)


            print(f"otp for {key}: {otp}")

            return Response({"message": "otp sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone_number")
        email = serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")

        identifier = phone or email
        key = f"otp: {identifier}"

        redis_conn = get_redis_connection("default")
        stored_otp = redis_conn.get(key)

        if stored_otp is None:
            return Response({"detail": "otp expierd or there is no any!"}, status=400)
        
        if stored_otp.decode() != otp:
            return Response({"detail": "incorrect otp"}, status=400)
        
        redis_conn.delete(key)
        return Response({"detail": "verified, u re in!"})