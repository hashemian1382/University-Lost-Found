from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import OTPRequest
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, 
    SetPasswordSerializer, UserProfileSerializer, ChangePasswordSerializer
)
from .utils import send_otp_email

User = get_user_model()

class SendOTPView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = OTPRequest.generate_otp()
            OTPRequest.objects.create(email=email, otp_code=otp)
            if not send_otp_email(email, otp):
                return Response({"error": "Failed to send OTP. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['otp_code']
            otp_obj = OTPRequest.objects.filter(email=email, otp_code=code, is_verified=False).order_by('-created_at').first()
            if otp_obj and otp_obj.is_valid():
                otp_obj.is_verified = True
                otp_obj.save()
                return Response({"message": "OTP verified"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['otp_code']
            password = serializer.validated_data['password']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']

            otp_obj = OTPRequest.objects.filter(email=email, otp_code=code, is_verified=True).order_by('-created_at').first()
            
            if otp_obj:
                user, created = User.objects.get_or_create(email=email)
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                otp_obj.delete()
                return Response({"message": "Account created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": "OTP not verified"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    def get_object(self):
        return self.request.user

class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
