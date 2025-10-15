"""
Custom authentication backend for JWT
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser


class SimpleUser:
    """Simple user object for JWT that doesn't require database"""
    def __init__(self, username, login_master_id=None, **kwargs):
        self.username = username
        self.login_master_id = login_master_id or username
        self.pk = login_master_id or username
        self.id = login_master_id or username
        self._is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False

        # Store additional attributes from token
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that doesn't query database for user"""

    def authenticate(self, request):
        """Authenticate the request and return a two-tuple of (user, token)."""
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # Validate token
        validated_token = self.get_validated_token(raw_token)

        # Get or create user from token
        user = self.get_user(validated_token)

        return user, validated_token

    def get_user(self, validated_token):
        """Override to return a simple user object without database query"""
        try:
            # validated_token is an AccessToken object, we can access values using get() or dict access
            # Get login_master_id from token (prioritize this)
            login_master_id = validated_token.get('login_master_id') if hasattr(validated_token, 'get') else None

            # Get username from token
            username = validated_token.get('username') if hasattr(validated_token, 'get') else None
            if not username:
                # Fallback to user_id
                username = validated_token.get('user_id') if hasattr(validated_token, 'get') else None
                if not username:
                    # If still no username, use login_master_id
                    username = str(login_master_id) if login_master_id else None

            # Ensure we have at least one identifier
            if not username and not login_master_id:
                # Log what we received for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"No user identifier in token. Token type: {type(validated_token)}, Token: {validated_token}")
                raise ValueError("No user identifier found in token")

            # Extract all relevant fields from token
            token_data = {}
            if hasattr(validated_token, 'get'):
                # Get role information - map role_id to role name
                role_id = validated_token.get('role_id')
                role = 'USER'  # Default role
                if role_id:
                    # Map role_id to role name based on common patterns
                    if role_id in [1, '1']:
                        role = 'ADMIN'
                    elif role_id in [2, '2']:
                        role = 'MERCHANT'
                    elif role_id in [3, '3']:
                        role = 'ACCOUNT_MANAGER'
                    elif role_id in [4, '4']:
                        role = 'BUSINESS_ANALYST'
                    else:
                        role = 'USER'

                token_data = {
                    'role_id': role_id,
                    'role': role,
                    'client_id': validated_token.get('client_id'),
                    'client_code': validated_token.get('client_code'),
                    'is_parent_merchant': validated_token.get('is_parent_merchant', False),
                }

            # Create simple user object with all token data
            user = SimpleUser(
                username=username or str(login_master_id),
                login_master_id=login_master_id,
                **token_data
            )

            # Add token data as user attributes for easy access
            if hasattr(validated_token, 'get'):
                # Store common token claims as user attributes
                setattr(user, 'user_id', validated_token.get('user_id'))
                setattr(user, 'exp', validated_token.get('exp'))
                setattr(user, 'iat', validated_token.get('iat'))

            return user
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JWT get_user error: {e}")
            # Raise InvalidToken to properly signal authentication failure
            from rest_framework_simplejwt.exceptions import InvalidToken
            raise InvalidToken("Unable to authenticate with provided token")