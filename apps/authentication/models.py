"""
Authentication models for user management
Using spclientonboard database with existing tables: login_master and lookup_role
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
import hashlib


class LookupRole(models.Model):
    """
    Existing lookup_role table in spclientonboard database
    This is an unmanaged model - we don't create/modify the table
    """

    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50)
    # role_description = models.TextField(blank=True, null=True)
    # is_active = models.BooleanField(default=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # Don't create migrations for this table
        db_table = "lookup_role"
        app_label = "authentication"

    def __str__(self):
        return self.role_name


class LoginMasterManager(BaseUserManager):
    """Manager for LoginMaster model"""

    def authenticate_user(self, username, password):
        """
        Custom authentication method for existing database
        Assumes password might be stored as MD5 or plain text in legacy system
        """
        try:
            # Try to find user by username
            user = self.get_queryset().filter(username=username).first()

            if not user:
                return None

            # Check password - handle different storage methods
            # Try MD5 hash first (common in legacy systems)
            md5_password = hashlib.md5(password.encode()).hexdigest()

            if user.password == password:  # Plain text (for legacy systems)
                return user
            elif user.password == md5_password:  # MD5 hash
                return user
            elif user.check_password(password):  # Django's method
                return user

            return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Authentication error: {e}")
            return None

    def create_user(self, username, email, password=None, **extra_fields):
        """Create a new user"""
        if not username:
            raise ValueError("Username is required")

        user = self.model(username=username, email=email, **extra_fields)
        if password:
            # For new users, use Django's password hashing
            user.set_password(password)
        user.save(using=self._db)
        return user


class LoginMaster(AbstractBaseUser):
    """
    Existing login_master table in spclientonboard database
    This is an unmanaged model that maps to the existing table
    """

    # Primary key - using username as primary key for JWT compatibility
    login_master_id = (
        models.IntegerField()
    )  # Commented out - may not exist in your table

    # Core authentication fields
    username = models.CharField(
        max_length=150, primary_key=True
    )  # Use username as primary key
    password = models.CharField(max_length=255)  # May contain MD5 or plain text
    email = models.EmailField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    # Role relationship (foreign key to lookup_role)
    role_id = models.IntegerField(default=2)  # Default to merchant role

    # Status fields
    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)

    # Merchant related fields
    # client_id = models.CharField(max_length=50, blank=True, null=True)
    # client_code = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    # Additional fields that might exist in your table
    # first_name = models.CharField(max_length=100, blank=True, null=True)
    # last_name = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_date = models.DateTimeField(default=timezone.now)
    # updated_at = models.DateTimeField(auto_now=True)
    last_login = None  # Override AbstractBaseUser's last_login field

    # Security fields
    # failed_login_attempts = models.IntegerField(default=0)
    # account_locked_until = models.DateTimeField(blank=True, null=True)

    objects = LoginMasterManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        managed = False  # Don't create migrations for this table
        db_table = "login_master"
        app_label = "authentication"

    def __str__(self):
        return self.username

    @property
    def id(self):
        """Return username as id for JWT compatibility"""
        return self.login_master_id

    @property
    def pk(self):
        """Return username as primary key"""
        return self.username

    @property
    def role(self):
        """Get role object"""
        try:
            return LookupRole.objects.get(role_id=self.role_id)
        except LookupRole.DoesNotExist:
            return None

    @property
    def role_name(self):
        """Get role name"""
        role = self.role
        return role.role_name if role else "UNKNOWN"

    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role_name in ["ADMIN", "Administrator", "admin"]

    @property
    def is_merchant(self):
        """Check if user is merchant"""
        return self.role_name in ["MERCHANT", "Merchant", "merchant"]

    def check_password(self, raw_password):
        """
        Check password against various formats
        Override to handle legacy password formats
        """
        # Check plain text (legacy)
        if self.password == raw_password:
            return True

        # Check MD5 (common in legacy systems)
        md5_password = hashlib.md5(raw_password.encode()).hexdigest()
        if self.password == md5_password:
            return True

        # Check Django's default method
        try:
            return super().check_password(raw_password)
        except (AttributeError, ValueError, TypeError):
            return False

    def has_perm(self, perm, obj=None):
        """Check if user has permission"""
        # Check if is_superuser attribute exists (for Django admin compatibility)
        if hasattr(self, 'is_superuser') and self.is_superuser:
            return True
        return self.is_admin

    def has_module_perms(self, app_label):
        """Check if user has permissions for app"""
        # Check if is_superuser attribute exists (for Django admin compatibility)
        if hasattr(self, 'is_superuser') and self.is_superuser:
            return True
        return self.is_admin


# Create a User alias for compatibility with views
User = LoginMaster


class UserSession(models.Model):
    """
    Track user sessions for security
    This is a new table we can create
    """

    user = models.ForeignKey(
        LoginMaster, on_delete=models.CASCADE, related_name="sessions"
    )
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    # is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "user_sessions"
        app_label = "authentication"

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"


class AuditLog(models.Model):
    """
    Comprehensive audit logging
    This is a new table we can create
    """

    user = models.ForeignKey(
        LoginMaster, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    response_status = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        app_label = "authentication"

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
