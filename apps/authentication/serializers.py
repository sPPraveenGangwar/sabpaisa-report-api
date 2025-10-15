"""
Serializers for authentication app
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, LookupRole, UserSession, AuditLog


class UserSerializer(serializers.ModelSerializer):
    """User serializer for API responses"""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'mobile', 'role', 'is_active',
            'client_id', 'client_code', 'merchant_name', 'allowed_zones',
            'is_parent_merchant', 'parent_merchant_id', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class LoginSerializer(serializers.Serializer):
    """Login serializer for authentication"""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError('Invalid credentials')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')

            if user.account_locked_until:
                import datetime
                if user.account_locked_until > datetime.datetime.now(datetime.timezone.utc):
                    raise serializers.ValidationError('Account is temporarily locked')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class TokenSerializer(serializers.Serializer):
    """Token response serializer"""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token serializer"""

    refresh = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")

        # Add password strength validation
        password = attrs['new_password']
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")

        return attrs


class LookupRoleSerializer(serializers.ModelSerializer):
    """Role serializer"""

    class Meta:
        model = LookupRole
        fields = '__all__'


class UserSessionSerializer(serializers.ModelSerializer):
    """User session serializer"""

    user = serializers.StringRelatedField()

    class Meta:
        model = UserSession
        fields = ('id', 'user', 'ip_address', 'user_agent', 'created_at', 'last_activity', 'is_active')


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer"""

    user = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ('checksum',)


class MerchantRegistrationSerializer(serializers.ModelSerializer):
    """Merchant registration serializer"""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'confirm_password', 'mobile',
            'client_code', 'merchant_name', 'allowed_zones'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")

        attrs.pop('confirm_password')
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'MERCHANT'
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user