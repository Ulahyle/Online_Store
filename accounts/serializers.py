from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from accounts.models import Customer
from django.db.models import Q


def validate_contact_info(data):
    phone = data.get('phone_number')
    email = data.get('email')
    if not phone and not email:
        raise serializers.ValidationError(
            _("Please enter your phone number or email.")
        )
    return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Customer
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return Customer.objects.create_user(**validated_data)


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, data):
        return validate_contact_info(data)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    otp = serializers.CharField()

    def validate(self, data):
        return validate_contact_info(data)


class OTPLoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, data):
        data = validate_contact_info(data)

        phone = data.get('phone_number')
        email = data.get('email')

        if not Customer.objects.filter(
            Q(phone_number=phone) | Q(email=email)
        ).exists():
            raise serializers.ValidationError(
                _("No account found with the provided credentials.")
            )

        return data
