"""
URL configuration for system monitoring endpoints
NEW ENDPOINTS - Do not modify existing API routes
"""
from django.urls import path
from apps.core.system_views import (
    SystemHealthView,
    SystemMetricsView,
    DatabaseStatusView,
    AuditLogView
)

urlpatterns = [
    # Health check endpoint - Public
    path('health/', SystemHealthView.as_view(), name='system-health'),

    # System metrics - Admin only
    path('metrics/', SystemMetricsView.as_view(), name='system-metrics'),

    # Database status - Admin only
    path('database/status/', DatabaseStatusView.as_view(), name='database-status'),

    # Audit logs - Admin only
    path('audit-logs/', AuditLogView.as_view(), name='audit-logs'),
]
