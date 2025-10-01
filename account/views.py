from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import random
import string

# JWT imports
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserAccount, UserOtp
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, OtpVerificationSerializer, OtpResendSerializer
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer to include additional user information"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['verified'] = user.verified
        
        # Add user account information
        try:
            user_account = UserAccount.objects.get(user=user)
            token['firstname'] = user_account.firstname
            token['lastname'] = user_account.lastname
            token['is_blocked'] = user_account.is_blocked
        except UserAccount.DoesNotExist:
            token['firstname'] = None
            token['lastname'] = None
            token['is_blocked'] = False
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'verified': self.user.verified,
        }
        
        # Add user account information
        try:
            user_account = UserAccount.objects.get(user=self.user)
            data['user'].update({
                'firstname': user_account.firstname,
                'lastname': user_account.lastname,
                'is_blocked': user_account.is_blocked,
            })
        except UserAccount.DoesNotExist:
            data['user'].update({
                'firstname': None,
                'lastname': None,
                'is_blocked': False,
            })
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT view with additional user information"""
    serializer_class = CustomTokenObtainPairSerializer


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp_code):
    """Send OTP via email"""
    subject = 'Joggle - Verification Code'
    message = f'Your verification code is: {otp_code}\n\nThis code will expire in 10 minutes.'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@joggle.com')
    
    try:
        send_mail(subject, message, from_email, [email])
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Check if user already exists
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user and user account
        user = serializer.save()
        
        # Automatically verify user (skip OTP for now)
        user.verified = True
        user.save()
        
        # # Generate OTP (COMMENTED OUT)
        # otp_code = generate_otp()
        # expire_time = datetime.now() + timedelta(minutes=10)
        # 
        # # Save OTP (COMMENTED OUT)
        # UserOtp.objects.filter(email=email).delete()  # Remove old OTPs
        # UserOtp.objects.create(
        #     email=email,
        #     code=otp_code,
        #     expire_at=expire_time
        # )
        # 
        # # Send OTP email (COMMENTED OUT)
        # if send_otp_email(email, otp_code):
        #     return Response(
        #         {
        #             'message': 'User registered successfully. Please check your email for verification code.',
        #             'user_id': user.id,
        #             'email': user.email
        #         },
        #         status=status.HTTP_201_CREATED
        #     )
        # else:
        #     return Response(
        #         {'error': 'Failed to send verification email'}, 
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
        
        return Response(
            {
                'message': 'User registered successfully. You can now login.',
                'user_id': user.id,
                'email': user.email,
                'verified': True
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP and activate user account"""
    serializer = OtpVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            # Get the latest OTP for this email
            user_otp = UserOtp.objects.filter(email=email).latest('created_at')
            
            # Check if OTP is valid and not expired
            if user_otp.code == otp_code and user_otp.expire_at > datetime.now():
                # Activate user account
                user = User.objects.get(email=email)
                user.verified = True
                user.save()
                
                # Delete used OTP
                user_otp.delete()
                
                return Response(
                    {'message': 'Email verified successfully. You can now login.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Invalid or expired OTP'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except UserOtp.DoesNotExist:
            return Response(
                {'error': 'No OTP found for this email'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """Resend OTP to user's email"""
    serializer = OtpResendSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate new OTP
            otp_code = generate_otp()
            expire_time = datetime.now() + timedelta(minutes=10)
            
            # Delete old OTPs and save new one
            UserOtp.objects.filter(email=email).delete()
            UserOtp.objects.create(
                email=email,
                code=otp_code,
                expire_at=expire_time
            )
            
            # Send OTP email
            if send_otp_email(email, otp_code):
                return Response(
                    {'message': 'OTP sent successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Failed to send OTP email'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login endpoint with JWT tokens"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if user is verified
        if not user.verified:
            return Response(
                {'error': 'Please verify your email before logging in'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user account is blocked
        try:
            user_account = UserAccount.objects.get(user=user)
            if user_account.is_blocked:
                return Response(
                    {'error': 'Your account has been blocked'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except UserAccount.DoesNotExist:
            pass
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Update login status
        try:
            user_account = UserAccount.objects.get(user=user)
            user_account.is_loggedin = True
            user_account.save()
        except UserAccount.DoesNotExist:
            pass
        
        return Response(
            {
                'message': 'Login successful',
                'access': str(access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'verified': user.verified,
                    'firstname': user_account.firstname if 'user_account' in locals() else None,
                    'lastname': user_account.lastname if 'user_account' in locals() else None,
                    'is_blocked': user_account.is_blocked if 'user_account' in locals() else False,
                }
            },
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """User logout endpoint with JWT token blacklisting"""
    try:
        # Get refresh token from request body
        refresh_token = request.data.get('refresh')
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Update login status
        try:
            user_account = UserAccount.objects.get(user=request.user)
            user_account.is_loggedin = False
            user_account.save()
        except UserAccount.DoesNotExist:
            pass
        
        return Response(
            {'message': 'Logout successful'}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Invalid token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveAPIView):
    """Get user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            return UserAccount.objects.get(user=self.request.user)
        except UserAccount.DoesNotExist:
            return None


class UserProfileUpdateView(generics.UpdateAPIView):
    """Update user profile"""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            return UserAccount.objects.get(user=self.request.user)
        except UserAccount.DoesNotExist:
            return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Check old password
        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'}, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request password reset"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP for password reset
            otp_code = generate_otp()
            expire_time = datetime.now() + timedelta(minutes=10)
            
            # Delete old OTPs and save new one
            UserOtp.objects.filter(email=email).delete()
            UserOtp.objects.create(
                email=email,
                code=otp_code,
                expire_at=expire_time
            )
            
            # Send OTP email
            if send_otp_email(email, otp_code):
                return Response(
                    {'message': 'Password reset OTP sent to your email'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Failed to send password reset email'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response(
                {'message': 'If the email exists, a password reset OTP has been sent'},
                status=status.HTTP_200_OK
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """Confirm password reset with OTP"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Get the latest OTP for this email
            user_otp = UserOtp.objects.filter(email=email).latest('created_at')
            
            # Check if OTP is valid and not expired
            if user_otp.code == otp_code and user_otp.expire_at > datetime.now():
                # Reset password
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Delete used OTP
                user_otp.delete()
                
                return Response(
                    {'message': 'Password reset successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Invalid or expired OTP'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except UserOtp.DoesNotExist:
            return Response(
                {'error': 'No OTP found for this email'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_status(request):
    """Get current user status"""
    try:
        user_account = UserAccount.objects.get(user=request.user)
        return Response({
            'user_id': request.user.id,
            'email': request.user.email,
            'verified': request.user.verified,
            'is_loggedin': user_account.is_loggedin,
            'is_blocked': user_account.is_blocked,
            'firstname': user_account.firstname,
            'lastname': user_account.lastname
        })
    except UserAccount.DoesNotExist:
        return Response({
            'user_id': request.user.id,
            'email': request.user.email,
            'verified': request.user.verified,
            'is_loggedin': False,
            'is_blocked': False
        })
