import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import RegisterSerializer, SendOTPSerializer
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