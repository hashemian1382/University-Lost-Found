from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTPRequest
import re

User = get_user_model()

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_password(self, value):
        """
        Check that the password is at least 8 characters long,
        contains at least one uppercase letter, one lowercase letter, and one number.
        """
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', value):
            raise serializers.ValidationError(
                "رمز عبور باید حداقل ۸ کاراکتر باشد و شامل حداقل یک حرف بزرگ، یک حرف کوچک و یک عدد باشد."
            )
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['email']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        """
        Check that the new password meets security requirements.
        """
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', value):
            raise serializers.ValidationError(
                "رمز عبور جدید باید حداقل ۸ کاراکتر باشد و شامل حداقل یک حرف بزرگ، یک حرف کوچک و یک عدد باشد."
            )
        return value
