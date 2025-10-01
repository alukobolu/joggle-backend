from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserAccount, UserOtp
import secrets
from datetime import datetime, timedelta


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    firstname = serializers.CharField(write_only=True, max_length=200)
    lastname = serializers.CharField(write_only=True, max_length=200)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'firstname', 'lastname')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm and profile fields from validated_data
        validated_data.pop('password_confirm')
        firstname = validated_data.pop('firstname')
        lastname = validated_data.pop('lastname')
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Create user account profile
        UserAccount.objects.create(
            user=user,
            firstname=firstname,
            lastname=lastname,
            email=user.email
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    email = serializers.EmailField(source='user.email', read_only=True)
    verified = serializers.BooleanField(source='user.verified', read_only=True)
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAccount
        fields = ('id', 'email', 'firstname', 'lastname', 'fullname', 'country', 
                 'phone', 'profile_image', 'verified', 'is_blocked')
        read_only_fields = ('id', 'email', 'verified')
    
    def get_fullname(self, obj):
        return obj.fullname()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = UserAccount
        fields = ('firstname', 'lastname', 'country', 'phone', 'profile_image')


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class OtpVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)


class OtpResendSerializer(serializers.Serializer):
    """Serializer for resending OTP"""
    email = serializers.EmailField()


class UserOtpSerializer(serializers.ModelSerializer):
    """Serializer for OTP model"""
    
    class Meta:
        model = UserOtp
        fields = ('email', 'expire_at')
        read_only_fields = ('email', 'expire_at')
