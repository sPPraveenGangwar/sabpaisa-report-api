"""
Custom permission classes for role-based access control
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin users only
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'ADMIN'
        )


class IsMerchant(permissions.BasePermission):
    """
    Permission check for merchant users
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ['MERCHANT', 'ADMIN']
        )

    def has_object_permission(self, request, view, obj):
        """
        Merchants can only access their own data
        """
        if getattr(request.user, 'role', None) == 'ADMIN':
            return True

        # Check if the object belongs to the merchant
        if hasattr(obj, 'merchant_id'):
            return obj.merchant_id == getattr(request.user, 'merchant_id', None)
        elif hasattr(obj, 'client_code'):
            return obj.client_code == getattr(request.user, 'client_code', None)

        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners or admins
    """
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if getattr(request.user, 'role', None) == 'ADMIN':
            return True

        # Check ownership
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False


class IsAccountManager(permissions.BasePermission):
    """
    Permission for account managers
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ['ACCOUNT_MANAGER', 'ADMIN']
        )


class IsBusinessAnalyst(permissions.BasePermission):
    """
    Permission for business analysts
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ['BUSINESS_ANALYST', 'ADMIN']
        )


class HasAPIAccess(permissions.BasePermission):
    """
    Check if user has API access enabled
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            getattr(request.user, 'api_access_enabled', True)
        )


class MerchantZonePermission(permissions.BasePermission):
    """
    Check merchant zone permissions (UserZoneMapper)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Admins have access to all zones
        if getattr(request.user, 'role', None) == 'ADMIN':
            return True

        # Check zone permissions
        zone = request.GET.get('zone') or request.data.get('zone')
        if zone:
            user_zones = getattr(request.user, 'allowed_zones', [])
            return zone in user_zones

        return True