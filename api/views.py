from django.utils import timezone
import random

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import User
from .serializers import UserRegistrationSerializer, UserChangePasswordSerializer, UserLoginSerializer, \
    UserProfileSerializer, UserUpdateSerializer, LogoutSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .utils import send_otp_email, send_password_email, success_false_response, success_true_response


# Create your views here.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'User updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data.get('access_token')
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)


from datetime import timedelta


class ValidateOTP(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        otp = request.data.get('otp', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'Failure': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            # Check if OTP is within the 30-second window
            time_difference = timezone.now() - user.otp_created_at
            if time_difference < timedelta(seconds=30):
                user.otp = None  # Reset the OTP field after successful validation
                user.save()

                token = get_tokens_for_user(user)
                return Response({'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({'Failure': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Failure': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginWithOTP(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        otp = random.randint(100000, 999999)
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_otp_email(email, otp)
        # send_otp_phone(phone_number, otp)

        return Response({'message': 'OTP has been sent to your email.'}, status=status.HTTP_200_OK)


class ResetPasswordWithOTP(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        new_password = request.data.get('new_password', '')
        otp = request.data.get('otp', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'Failure': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            # Check if OTP is within the 30-second window
            time_difference = timezone.now() - user.otp_created_at
            if time_difference < timedelta(seconds=30):
                user.set_password(new_password)
                user.otp = None  # Reset the OTP field after successful password reset
                user.save()
                return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
            else:
                return Response({'Failure': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Failure': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
