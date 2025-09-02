import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_redis import get_redis_connection
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.models import Customer, Address

from accounts.serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    OTPLoginRequestSerializer,
    CustomerProfileSerializer,
    AddressSerializer
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
            return Response({"detail": "OTP expired or does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if stored_otp.decode() != otp:
            return Response({"detail": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

        redis_conn.delete(key)

        try:
            # a query that works for either phone or email
            query = Q()
            if phone:
                query |= Q(phone_number=phone)
            if email:
                query |= Q(email=email)
            
            user = Customer.objects.get(query)
        except Customer.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

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

        otp = str(random.randint(100000, 999999))
        key = f"otp:{identifier}"

        redis_conn = get_redis_connection("default")
        redis_conn.setex(key, 360, otp)

        print(f"OTP for {identifier}: {otp}")
        return Response({"detail": "Code sent!"}, status=200)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # returns only the addresses of the currently authenticated user
        return Address.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # automatically assigns the current user to the address
        serializer.save(customer=self.request.user)

class CustomerProfileView(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # returns the authenticated user's profile
        return self.request.user
