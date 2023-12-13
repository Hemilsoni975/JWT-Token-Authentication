import re
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from api.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.contrib.auth import get_user_model


class UserRegistrationSerializer(serializers.ModelSerializer):
    # We are writing this because we need confirm password field in our Registration Request
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'firstname', 'lastname', 'contact', 'address', 'city', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Validate password using Django's built-in validators
        validate_password(data['password'], self.instance)

        # Additional custom password rules
        if len(data['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        # Check for at least one alphabet, one number, and one special character
        if not any(char.isalpha() for char in data['password']):
            raise serializers.ValidationError("Password must contain at least one alphabet.")
        if not any(char.isdigit() for char in data['password']):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', data['password']):
            raise serializers.ValidationError("Password must contain at least one special character.")

        # Confirm password check
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'firstname','lastname','password']


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        user.set_password(password)
        user.save()
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'contact', 'address', 'city']

    def update(self, instance, validated_data):
        # Update and save the instance with the validated data
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.contact = validated_data.get('contact', instance.contact)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)

        instance.save()
        return instance


class LogoutSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    # We are writing this because we need confirm password field in our Registration Request
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'otp']
        extra_kwargs = {
            'password': {'write_only': True}
        }