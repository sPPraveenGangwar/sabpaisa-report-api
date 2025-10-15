"""
URL patterns for authentication app
"""
from django.urls import path
from .views import (
    LoginView, LogoutView, TokenRefreshView,
    ChangePasswordView, ProfileView, UserSessionListView,
    UserSessionDetailView,
    RoleListView, health_check
)

app_name = 'authentication'

urlpatterns = [
    # JWT Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User Management
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Session Management
    path('sessions/', UserSessionListView.as_view(), name='sessions'),
    path('sessions/<str:session_id>/', UserSessionDetailView.as_view(), name='session-detail'),

    # Roles (Admin only)
    path('roles/', RoleListView.as_view(), name='roles'),

    # Health Check
    path('health/', health_check, name='health'),
]