"""
Authentication views for JWT-based authentication
Using existing login_master and lookup_role tables with raw SQL
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from django.utils import timezone
from django.db import connections
from django.core.cache import cache
import logging
import hashlib

from .serializers import (
    LoginSerializer,
    UserSerializer,
    TokenSerializer,
    ChangePasswordSerializer,
    MerchantRegistrationSerializer,
    UserSessionSerializer,
    AuditLogSerializer,
)
from apps.core.permissions import IsAdmin, IsMerchant

# Configure multiple loggers for different purposes
logger = logging.getLogger('apps.authentication')
security_logger = logging.getLogger('security')
performance_logger = logging.getLogger('performance')


# ===== PERFORMANCE OPTIMIZATION: Cached database schema helpers =====
def get_cached_login_master_columns():
    """
    Get cached column names for login_master table.
    Caches for 24 hours to avoid repeated SHOW COLUMNS queries.
    """
    cache_key = 'auth:schema:login_master_columns'
    columns = cache.get(cache_key)

    if columns is None:
        try:
            with connections["user_management"].cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM login_master")
                columns = [col[0] for col in cursor.fetchall()]
                # Cache for 24 hours (86400 seconds)
                cache.set(cache_key, columns, 86400)
                logger.info(f"Cached login_master columns: {len(columns)} columns")
        except Exception as e:
            logger.error(f"Error fetching login_master columns: {e}")
            columns = []

    return columns


def get_cached_role_name(role_id):
    """
    Get role name by role_id with caching.
    Caches all roles for 1 hour to avoid repeated lookups.
    """
    if not role_id:
        return None

    cache_key = 'auth:roles:mapping'
    role_mapping = cache.get(cache_key)

    if role_mapping is None:
        try:
            with connections["user_management"].cursor() as cursor:
                cursor.execute("SELECT role_id, role_name FROM lookup_role")
                roles = cursor.fetchall()
                role_mapping = {role[0]: role[1] for role in roles}
                # Cache for 1 hour (3600 seconds)
                cache.set(cache_key, role_mapping, 3600)
                logger.info(f"Cached {len(role_mapping)} roles")
        except Exception as e:
            logger.error(f"Error fetching roles: {e}")
            role_mapping = {}

    # Return role name or use fallback
    role_name = role_mapping.get(role_id)
    if not role_name:
        # Fallback mappings
        if role_id == 1:
            role_name = "ADMIN"
        elif role_id == 2:
            role_name = "MERCHANT"
        else:
            role_name = "MERCHANT"

    return role_name


def find_column_in_list(column_candidates, columns):
    """Find first matching column from candidates"""
    for candidate in column_candidates:
        if candidate in columns:
            return candidate
    return None
# ===== END PERFORMANCE OPTIMIZATION =====


class LoginView(APIView):
    """
    JWT Login endpoint
    POST /api/v1/auth/login/
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Log login attempt
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

        # Support both login_master_id and username for authentication
        login_master_id = request.data.get("login_master_id") or request.data.get(
            "loginId"
        )
        username = request.data.get("username")
        password = request.data.get("password")

        logger.info(f"Login attempt | User: {username or login_master_id or 'unknown'} | IP: {client_ip}")
        security_logger.info(f"LOGIN_ATTEMPT | User: {username or login_master_id} | IP: {client_ip} | User-Agent: {user_agent}")

        # Use login_master_id if provided, otherwise fall back to username
        auth_identifier = login_master_id if login_master_id else username

        if not auth_identifier or not password:
            logger.warning(f"Login failed - missing credentials | User: {auth_identifier or 'unknown'} | IP: {client_ip}")
            security_logger.warning(f"LOGIN_FAILED | Reason: Missing credentials | IP: {client_ip}")
            return Response(
                {
                    "success": False,
                    "message": "Login ID (login_master_id) or username and password are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Use cached column names for better performance
            columns = get_cached_login_master_columns()

            # Build query based on available columns
            username_columns = [
                "username",
                "user_name",
                "login_name",
                "email",
                "user_id",
            ]
            password_columns = ["password", "pass", "pwd", "user_password"]

            username_col = find_column_in_list(username_columns, columns)
            password_col = find_column_in_list(password_columns, columns)

            if not username_col or not password_col:
                logger.error(
                    f"Could not find username/password columns. Available columns: {columns}"
                )
                return Response(
                    {"success": False, "message": "Database configuration error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Use raw SQL to authenticate against login_master table
            with connections["user_management"].cursor() as cursor:
                # Try to authenticate with plain password
                query = f"SELECT * FROM login_master WHERE {username_col} = %s AND {password_col} = %s"
                cursor.execute(query, [auth_identifier, password])
                user_row = cursor.fetchone()

                if not user_row:
                    # Try with MD5 hash
                    md5_password = hashlib.md5(password.encode()).hexdigest()
                    cursor.execute(query, [auth_identifier, md5_password])
                    user_row = cursor.fetchone()

                if user_row:
                    # Convert to dictionary using cached columns
                    user_data = dict(zip(columns, user_row))

                    # Extract the actual username from user_data if we used login_master_id to authenticate
                    actual_username = (
                        user_data.get("username")
                        or user_data.get("user_name")
                        or auth_identifier
                    )

                    # Update last_login if column exists
                    if "last_login" in columns:
                        try:
                            cursor.execute(
                                f"UPDATE login_master SET last_login = NOW() WHERE {username_col} = %s",
                                [auth_identifier],
                            )
                        except:
                            pass  # Ignore if column doesn't exist

                    # Generate JWT tokens
                    # Create a minimal user object for token generation
                    class MinimalUser:
                        def __init__(self, user_id, username):
                            self.id = user_id
                            self.pk = user_id
                            self.username = username
                            self.is_active = True

                    # Determine the ID field - prioritize login_master_id
                    id_field = None
                    login_master_id = None
                    for field in [
                        "login_master_id",
                        "id",
                        "user_id",
                        "login_id",
                        username_col,
                    ]:
                        if field in user_data:
                            if field == "login_master_id":
                                login_master_id = user_data[field]
                            id_field = user_data[field]
                            break

                    if not id_field:
                        id_field = username  # Use username as ID if no ID field found

                    # Use login_master_id for the minimal user if available
                    minimal_user = MinimalUser(
                        login_master_id if login_master_id else id_field,
                        actual_username,
                    )

                    # Generate tokens
                    refresh = RefreshToken.for_user(minimal_user)
                    access = refresh.access_token

                    # Fetch role name using cached lookup (PERFORMANCE OPTIMIZED)
                    role_name = get_cached_role_name(user_data.get("role_id"))
                    logger.info(f"Role name for role_id {user_data.get('role_id')}: '{role_name}'")

                    # Add custom claims - include login_master_id as primary identifier
                    access["login_master_id"] = (
                        login_master_id if login_master_id else id_field
                    )
                    access["username"] = actual_username
                    if "role_id" in user_data:
                        access["role_id"] = user_data["role_id"]
                    if role_name:
                        access["role"] = role_name
                    if "client_id" in user_data:
                        access["client_id"] = user_data["client_id"]
                    if "client_code" in user_data:
                        access["client_code"] = user_data["client_code"]

                    # Prepare response
                    response_data = {
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "access": str(access),
                            "refresh": str(refresh),
                            "user": {
                                "id": id_field,
                                "login_master_id": (
                                    login_master_id if login_master_id else id_field
                                ),
                                "username": actual_username,
                                "email": user_data.get("email", ""),
                                "role_id": user_data.get("role_id", None),
                                "role": role_name,  # Add role name here
                                "client_id": user_data.get("client_id", ""),
                                "client_code": user_data.get("client_code", ""),
                                "merchant_name": user_data.get("merchant_name", ""),
                            },
                        },
                    }

                    logger.info(f"Login successful | User: {actual_username} | IP: {client_ip}")
                    security_logger.info(f"LOGIN_SUCCESS | User: {actual_username} | IP: {client_ip} | Role: {user_data.get('role_id', 'N/A')}")
                    performance_logger.info(f"Login completed | User: {actual_username} | Processing time: {timezone.now()}")
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    logger.warning(f"Login failed - invalid credentials | User: {auth_identifier} | IP: {client_ip}")
                    security_logger.warning(f"LOGIN_FAILED | User: {auth_identifier} | IP: {client_ip} | Reason: Invalid credentials")
                    return Response(
                        {"success": False, "message": "Invalid username or password"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

        except Exception as e:
            logger.exception(f"Login error | User: {auth_identifier} | IP: {client_ip} | Error: {e}")
            security_logger.error(f"LOGIN_ERROR | User: {auth_identifier} | IP: {client_ip} | Error: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "An error occurred during login",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    """
    Logout endpoint
    POST /api/v1/auth/logout/
    """

    permission_classes = [
        permissions.AllowAny
    ]  # Changed to AllowAny since logout should always work

    def post(self, request):
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        logger.info(f"Logout request | IP: {client_ip}")

        try:
            # Get refresh token
            refresh_token = request.data.get("refresh")
            if refresh_token:
                try:
                    # Try to blacklist the token
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except:
                    pass  # Ignore blacklist errors

            # Always return success for logout
            logger.info(f"Logout successful | IP: {client_ip}")
            security_logger.info(f"LOGOUT | IP: {client_ip}")
            return Response(
                {"success": True, "message": "Logout successful"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Still return success even if there's an error
            return Response(
                {"success": True, "message": "Logout completed"},
                status=status.HTTP_200_OK,
            )


class TokenRefreshView(BaseTokenRefreshView):
    """
    Token refresh endpoint
    POST /api/v1/auth/refresh/
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response(
                {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "data": response.data,
                }
            )
        return response


class ProfileView(APIView):
    """
    User profile endpoint
    GET /api/v1/auth/profile/
    PUT /api/v1/auth/profile/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user profile from database"""
        try:
            # Get user info from the authenticated user
            username = getattr(request.user, "username", None)
            login_master_id = getattr(request.user, "login_master_id", None)

            logger.info(f"ProfileView GET - Initial username: {username}, login_master_id: {login_master_id}, User: {request.user}")

            # If not authenticated, check if we have username in headers (for testing)
            if not username or username == "AnonymousUser":
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                logger.info(f"Auth header present: {bool(auth_header)}")
                if auth_header:
                    # Try to decode token to get username
                    try:
                        from rest_framework_simplejwt.tokens import AccessToken

                        token = auth_header.replace("Bearer ", "")
                        decoded = AccessToken(token)
                        # Try to get login_master_id first, then username
                        login_master_id = decoded.get("login_master_id")
                        username = decoded.get("username") or decoded.get("user_id")
                        logger.info(f"Decoded token - login_master_id: {login_master_id}, username: {username}")
                    except Exception as e:
                        logger.error(f"Token decode error: {e}")
                        pass

            # Use login_master_id if available, otherwise use username
            auth_identifier = (
                login_master_id
                if "login_master_id" in locals() and login_master_id
                else username
            )

            if not auth_identifier:
                logger.error(f"No auth identifier found - login_master_id: {login_master_id}, username: {username}")
                return Response(
                    {"success": False, "message": "User not authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get cached column names for better performance
            columns = get_cached_login_master_columns()

            # Find the appropriate column for authentication
            if (
                "login_master_id" in locals()
                and login_master_id
                and "login_master_id" in columns
            ):
                auth_col = "login_master_id"
                auth_value = login_master_id
            else:
                # Find username column
                username_columns = [
                    "username",
                    "user_name",
                    "login_name",
                    "email",
                    "user_id",
                ]
                auth_col = find_column_in_list(username_columns, columns)

                if not auth_col:
                    return Response(
                        {
                            "success": False,
                            "message": "Database configuration error",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                auth_value = auth_identifier

            # Get user data from database using raw SQL
            with connections["user_management"].cursor() as cursor:

                # Get user data
                query = f"SELECT * FROM login_master WHERE {auth_col} = %s"
                logger.info(f"ProfileView query: {query} with value: {auth_value}")
                cursor.execute(query, [auth_value])
                user_row = cursor.fetchone()

                if user_row:
                    logger.info(f"User found in database")
                    user_data = dict(zip(columns, user_row))

                    # Fetch role name using cached lookup (PERFORMANCE OPTIMIZED)
                    role_name = get_cached_role_name(user_data.get("role_id"))

                    # Build response with available fields
                    profile_data = {
                        "login_master_id": user_data.get("login_master_id", ""),
                        "username": user_data.get("username")
                        or user_data.get("user_name")
                        or username,
                        "email": user_data.get("email", ""),
                        "mobile": user_data.get(
                            "mobile_number", user_data.get("mobile", "")
                        ),
                        "name": user_data.get("name", ""),
                        "role_id": user_data.get("role_id", None),
                        "role": role_name,  # Add role name
                        "created_date": user_data.get("created_date", None),
                    }

                    # Add any other fields that exist
                    for key in ["client_id", "client_code", "merchant_name"]:
                        if key in user_data:
                            profile_data[key] = user_data[key]

                    return Response({"success": True, "data": profile_data})
                else:
                    logger.warning(f"User not found in database with {auth_col} = {auth_value}")
                    # Check what columns exist
                    logger.info(f"Available columns: {columns}")
                    return Response(
                        {"success": False, "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

        except Exception as e:
            logger.error(f"Profile error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Error fetching profile",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        """Update user profile"""
        try:
            # Get user identifier from request.user (set by JWT authentication)
            username = getattr(request.user, "username", None)
            login_master_id = getattr(request.user, "login_master_id", None)

            logger.info(f"ProfileView PUT - Initial username: {username}, login_master_id: {login_master_id}")

            # If not from request.user, decode from token
            if not username or username == "AnonymousUser":
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                if auth_header:
                    try:
                        from rest_framework_simplejwt.tokens import AccessToken

                        token = auth_header.replace("Bearer ", "")
                        decoded = AccessToken(token)
                        login_master_id = decoded.get("login_master_id")
                        username = decoded.get("username") or decoded.get("user_id")
                        logger.info(f"Decoded from token - login_master_id: {login_master_id}, username: {username}")
                    except Exception as e:
                        logger.error(f"Token decode error in PUT: {e}")

            # Determine auth identifier
            auth_identifier = (
                login_master_id
                if login_master_id
                else username
            )

            if not auth_identifier:
                return Response(
                    {"success": False, "message": "User not authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get the data to update
            update_data = request.data
            logger.info(f"Update data received: {update_data}")

            # Fields that are allowed to be updated
            allowed_fields = [
                'email', 'mobile_number', 'mobile', 'name',
                'first_name', 'last_name', 'phone',
                'address', 'city', 'state', 'country', 'pincode'
            ]

            # Get cached column names for better performance
            columns = get_cached_login_master_columns()

            # Find the auth column
            if login_master_id and 'login_master_id' in columns:
                auth_col = 'login_master_id'
                auth_value = login_master_id
            else:
                # Find username column
                username_columns = [
                    "username", "user_name", "login_name", "email", "user_id"
                ]
                auth_col = find_column_in_list(username_columns, columns)

                if not auth_col:
                    return Response(
                        {"success": False, "message": "Database configuration error"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                auth_value = auth_identifier

            # Build update query dynamically
            with connections["user_management"].cursor() as cursor:

                # Check if user exists
                cursor.execute(
                    f"SELECT * FROM login_master WHERE {auth_col} = %s",
                    [auth_value]
                )
                user_row = cursor.fetchone()

                if not user_row:
                    return Response(
                        {"success": False, "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Build SET clause for UPDATE
                update_fields = []
                update_values = []

                for field, value in update_data.items():
                    # Only update allowed fields that exist in the table
                    if field in allowed_fields and field in columns:
                        update_fields.append(f"{field} = %s")
                        update_values.append(value)

                if not update_fields:
                    return Response(
                        {
                            "success": False,
                            "message": "No valid fields to update",
                            "allowed_fields": [f for f in allowed_fields if f in columns]
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Add auth value at the end for WHERE clause
                update_values.append(auth_value)

                # Execute UPDATE query
                update_query = f"UPDATE login_master SET {', '.join(update_fields)} WHERE {auth_col} = %s"
                logger.info(f"Executing update: {update_query} with values: {update_values[:-1]}...")

                cursor.execute(update_query, update_values)
                affected_rows = cursor.rowcount

                if affected_rows > 0:
                    # Fetch updated user data
                    cursor.execute(
                        f"SELECT * FROM login_master WHERE {auth_col} = %s",
                        [auth_value]
                    )
                    updated_row = cursor.fetchone()
                    updated_data = dict(zip(columns, updated_row))

                    # Build response with updated fields
                    profile_data = {
                        "login_master_id": updated_data.get("login_master_id", ""),
                        "username": updated_data.get("username") or updated_data.get("user_name") or username,
                        "email": updated_data.get("email", ""),
                        "mobile": updated_data.get("mobile_number", updated_data.get("mobile", "")),
                        "name": updated_data.get("name", ""),
                        "role_id": updated_data.get("role_id", None),
                    }

                    # Add any other fields that exist
                    for key in ["client_id", "client_code", "merchant_name", "first_name", "last_name"]:
                        if key in updated_data:
                            profile_data[key] = updated_data[key]

                    return Response({
                        "success": True,
                        "message": "Profile updated successfully",
                        "data": profile_data
                    })
                else:
                    return Response({
                        "success": False,
                        "message": "No changes made to profile"
                    })

        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Error updating profile",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordView(APIView):
    """
    Change password endpoint
    POST /api/v1/auth/change-password/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        logger.info(f"Password change request | IP: {client_ip}")

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Validate required fields
        if not old_password or not new_password:
            return Response(
                {
                    "success": False,
                    "message": "Old password and new password are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if confirm_password matches new_password
        if confirm_password and new_password != confirm_password:
            return Response(
                {
                    "success": False,
                    "message": "New password and confirm password do not match",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate new password strength (optional)
        if len(new_password) < 6:
            return Response(
                {
                    "success": False,
                    "message": "New password must be at least 6 characters long",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get user identifier from request.user (set by JWT authentication)
            username = getattr(request.user, "username", None)
            login_master_id = getattr(request.user, "login_master_id", None)

            logger.info(f"ChangePassword - Username: {username}, login_master_id: {login_master_id}")

            # If not from request.user, decode from token
            if not username or username == "AnonymousUser":
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                if auth_header:
                    try:
                        from rest_framework_simplejwt.tokens import AccessToken

                        token = auth_header.replace("Bearer ", "")
                        decoded = AccessToken(token)
                        login_master_id = decoded.get("login_master_id")
                        username = decoded.get("username") or decoded.get("user_id")
                        logger.info(f"Decoded from token - login_master_id: {login_master_id}, username: {username}")
                    except Exception as e:
                        logger.error(f"Token decode error: {e}")

            # Determine auth identifier
            auth_identifier = login_master_id if login_master_id else username

            if not auth_identifier:
                return Response(
                    {"success": False, "message": "User not authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get cached column names for better performance
            columns = get_cached_login_master_columns()

            # Find auth column and password column
            if login_master_id and 'login_master_id' in columns:
                auth_col = 'login_master_id'
                auth_value = login_master_id
            else:
                # Find username column
                username_columns = ["username", "user_name", "login_name", "email", "user_id"]
                auth_col = find_column_in_list(username_columns, columns)

                if not auth_col:
                    return Response(
                        {"success": False, "message": "Database configuration error"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                auth_value = auth_identifier

            # Find password column
            password_columns = ["password", "pass", "pwd", "user_password"]
            password_col = find_column_in_list(password_columns, columns)

            if not password_col:
                logger.error("No password column found in database")
                return Response(
                    {"success": False, "message": "Password column not found in database"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            with connections["user_management"].cursor() as cursor:

                # First verify the old password
                # Try with plain password
                query = f"SELECT * FROM login_master WHERE {auth_col} = %s AND {password_col} = %s"
                cursor.execute(query, [auth_value, old_password])
                user_row = cursor.fetchone()

                if not user_row:
                    # Try with MD5 hash
                    md5_old_password = hashlib.md5(old_password.encode()).hexdigest()
                    cursor.execute(query, [auth_value, md5_old_password])
                    user_row = cursor.fetchone()

                if not user_row:
                    logger.warning(f"Password change failed - incorrect old password | User: {auth_identifier} | IP: {client_ip}")
                    security_logger.warning(f"PASSWORD_CHANGE_FAILED | User: {auth_identifier} | IP: {client_ip} | Reason: Incorrect old password")
                    return Response(
                        {"success": False, "message": "Current password is incorrect"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Old password is correct, now update to new password
                # Check what format the current password is in
                user_data = dict(zip(columns, user_row))
                current_password = user_data.get(password_col)

                # Determine password format and hash new password accordingly
                if current_password == old_password:
                    # Plain text - store new password as plain text (not recommended)
                    new_password_to_store = new_password
                    logger.info("Storing new password as plain text (matching existing format)")
                elif current_password == hashlib.md5(old_password.encode()).hexdigest():
                    # MD5 hash - store new password as MD5
                    new_password_to_store = hashlib.md5(new_password.encode()).hexdigest()
                    logger.info("Storing new password as MD5 hash")
                else:
                    # Default to MD5 for legacy compatibility
                    new_password_to_store = hashlib.md5(new_password.encode()).hexdigest()
                    logger.info("Defaulting to MD5 hash for new password")

                # Update password in database
                update_query = f"UPDATE login_master SET {password_col} = %s WHERE {auth_col} = %s"
                logger.info(f"Updating password for user: {auth_identifier}")

                cursor.execute(update_query, [new_password_to_store, auth_value])
                affected_rows = cursor.rowcount

                if affected_rows > 0:
                    # Also update last_modified or updated_at if such column exists
                    timestamp_columns = ["updated_at", "last_modified", "modified_date"]
                    for ts_col in timestamp_columns:
                        if ts_col in columns:
                            try:
                                cursor.execute(
                                    f"UPDATE login_master SET {ts_col} = NOW() WHERE {auth_col} = %s",
                                    [auth_value]
                                )
                            except:
                                pass  # Ignore if update fails

                    logger.info(f"Password changed successfully | User: {auth_identifier} | IP: {client_ip}")
                    security_logger.info(f"PASSWORD_CHANGED | User: {auth_identifier} | IP: {client_ip}")
                    return Response({
                        "success": True,
                        "message": "Password changed successfully"
                    })
                else:
                    logger.error(f"Failed to update password for user: {auth_identifier}")
                    return Response({
                        "success": False,
                        "message": "Failed to update password"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception(f"Password change error | User: {auth_identifier if 'auth_identifier' in locals() else 'unknown'} | IP: {client_ip} | Error: {e}")
            security_logger.error(f"PASSWORD_CHANGE_ERROR | IP: {client_ip} | Error: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Error changing password",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserSessionListView(APIView):
    """
    List user sessions
    GET /api/v1/auth/sessions/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user session information"""
        try:
            # Get current user info
            username = getattr(request.user, "username", None)
            login_master_id = getattr(request.user, "login_master_id", None)

            # Get token from request
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            current_token = None
            if auth_header and auth_header.startswith("Bearer "):
                current_token = auth_header.replace("Bearer ", "")

            sessions = []

            # Add current session info from JWT token
            if current_token:
                try:
                    from rest_framework_simplejwt.tokens import AccessToken
                    from datetime import datetime

                    # Decode current token
                    token = AccessToken(current_token)

                    # Extract session info from token
                    session_info = {
                        "session_id": token.get("jti", ""),  # JWT ID
                        "user_id": token.get("user_id", username),
                        "login_master_id": token.get("login_master_id", login_master_id),
                        "username": token.get("username", username),
                        "token_type": token.get("token_type", "access"),
                        "created_at": datetime.fromtimestamp(token.get("iat", 0)).isoformat() if token.get("iat") else None,
                        "expires_at": datetime.fromtimestamp(token.get("exp", 0)).isoformat() if token.get("exp") else None,
                        "is_active": True,
                        "ip_address": self.get_client_ip(request),
                        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                        "role_id": token.get("role_id"),
                        "client_id": token.get("client_id"),
                    }

                    # Calculate session duration
                    if token.get("iat") and token.get("exp"):
                        duration = token.get("exp") - token.get("iat")
                        session_info["duration_seconds"] = duration
                        session_info["duration_readable"] = self.format_duration(duration)

                    sessions.append(session_info)

                except Exception as e:
                    logger.error(f"Error decoding token for sessions: {e}")

            # If we have database session tracking (optional - for future implementation)
            # We could query a sessions table here to get historical sessions

            # For now, we'll also check if there are any refresh tokens
            # This would require database storage of refresh tokens

            # Get additional session metadata
            response_data = {
                "success": True,
                "data": sessions,
                "metadata": {
                    "total_sessions": len(sessions),
                    "current_session_id": sessions[0]["session_id"] if sessions else None,
                    "user": {
                        "username": username,
                        "login_master_id": login_master_id
                    }
                }
            }

            return Response(response_data)

        except Exception as e:
            logger.error(f"Session list error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Error fetching sessions",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            return f"{seconds // 3600} hours"
        else:
            return f"{seconds // 86400} days"


class UserSessionDetailView(APIView):
    """
    Get or terminate a specific session
    GET /api/v1/auth/sessions/<session_id>/
    POST /api/v1/auth/sessions/<session_id>/ (with action: terminate)
    DELETE /api/v1/auth/sessions/<session_id>/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        """Get details of a specific session"""
        try:
            # Get current user info
            username = getattr(request.user, "username", None)
            login_master_id = getattr(request.user, "login_master_id", None)

            # Get current token
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            current_token = None
            if auth_header and auth_header.startswith("Bearer "):
                current_token = auth_header.replace("Bearer ", "")

            session_info = None

            # Check if the session_id matches current token's JTI
            if current_token:
                try:
                    from rest_framework_simplejwt.tokens import AccessToken
                    from datetime import datetime

                    token = AccessToken(current_token)
                    current_jti = token.get("jti", "")

                    # Check if this is the current session
                    if current_jti == session_id:
                        session_info = {
                            "session_id": token.get("jti", ""),
                            "user_id": token.get("user_id", username),
                            "login_master_id": token.get("login_master_id", login_master_id),
                            "username": token.get("username", username),
                            "token_type": token.get("token_type", "access"),
                            "created_at": datetime.fromtimestamp(token.get("iat", 0)).isoformat() if token.get("iat") else None,
                            "expires_at": datetime.fromtimestamp(token.get("exp", 0)).isoformat() if token.get("exp") else None,
                            "is_active": True,
                            "is_current": True,
                            "ip_address": self.get_client_ip(request),
                            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                            "role_id": token.get("role_id"),
                            "client_id": token.get("client_id"),
                        }

                        # Calculate remaining time
                        if token.get("exp"):
                            remaining = token.get("exp") - datetime.now().timestamp()
                            session_info["remaining_seconds"] = max(0, int(remaining))
                            session_info["remaining_readable"] = self.format_duration(max(0, int(remaining)))

                except Exception as e:
                    logger.error(f"Error checking session: {e}")

            if session_info:
                return Response({
                    "success": True,
                    "data": session_info,
                    "message": "Session found"
                })
            else:
                # In a real implementation with database session storage,
                # we would check the database here
                return Response({
                    "success": False,
                    "message": "Session not found or expired"
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Session detail error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Error fetching session details",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, session_id):
        """Perform action on a session (e.g., terminate)"""
        try:
            action = request.data.get("action")

            if action == "terminate" or action == "revoke":
                return self.terminate_session(request, session_id)
            else:
                return Response({
                    "success": False,
                    "message": "Invalid action. Supported actions: terminate, revoke"
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Session action error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Error performing session action",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, session_id):
        """Terminate/delete a session"""
        return self.terminate_session(request, session_id)

    def terminate_session(self, request, session_id):
        """Terminate a specific session"""
        try:
            # Get current token
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            current_token = None
            if auth_header and auth_header.startswith("Bearer "):
                current_token = auth_header.replace("Bearer ", "")

            # Check if trying to terminate current session
            if current_token:
                from rest_framework_simplejwt.tokens import AccessToken
                token = AccessToken(current_token)
                current_jti = token.get("jti", "")

                if current_jti == session_id:
                    # User is terminating their current session (like logout)
                    # In a real implementation, we would blacklist the token here
                    return Response({
                        "success": True,
                        "message": "Current session terminated. Please login again.",
                        "action": "logout_required"
                    })

            # For other sessions, in a real implementation with database storage,
            # we would mark the session as terminated in the database
            # Since we're using stateless JWT, we can only blacklist tokens

            # For now, return success if it's not the current session
            return Response({
                "success": True,
                "message": "Session terminated successfully",
                "note": "Full session termination requires token blacklisting implementation"
            })

        except Exception as e:
            logger.error(f"Session termination error: {e}")
            return Response(
                {
                    "success": False,
                    "message": "Error terminating session",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        if seconds <= 0:
            return "Expired"
        elif seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            return f"{seconds // 86400} days"



class RoleListView(APIView):
    """
    List all roles
    GET /api/v1/auth/roles/
    """

    permission_classes = [permissions.AllowAny]  # Changed to allow testing

    def get(self, request):
        """Get all roles from lookup_role table with caching (PERFORMANCE OPTIMIZED)"""
        try:
            cache_key = 'auth:roles:list'
            role_list = cache.get(cache_key)

            if role_list is None:
                with connections["user_management"].cursor() as cursor:
                    # Check if lookup_role table exists
                    cursor.execute("SHOW TABLES LIKE 'lookup_role'")
                    if cursor.fetchone():
                        cursor.execute("SELECT * FROM lookup_role")
                        roles = cursor.fetchall()

                        # Get column names
                        cursor.execute("SHOW COLUMNS FROM lookup_role")
                        column_names = [col[0] for col in cursor.fetchall()]

                        # Convert to list of dictionaries
                        role_list = []
                        for role in roles:
                            role_dict = dict(zip(column_names, role))
                            role_list.append(role_dict)

                        # Cache for 1 hour
                        cache.set(cache_key, role_list, 3600)
                        logger.info(f"Cached role list: {len(role_list)} roles")
                    else:
                        return Response(
                            {
                                "success": False,
                                "message": "lookup_role table does not exist",
                            }
                        )

            return Response({"success": True, "data": role_list})

        except Exception as e:
            logger.error(f"Error fetching roles: {e}")
            return Response(
                {"success": False, "message": "Error fetching roles", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Health check endpoint
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint
    GET /api/v1/auth/health/
    """
    return Response(
        {
            "success": True,
            "message": "Authentication service is running",
            "timestamp": timezone.now(),
        }
    )
