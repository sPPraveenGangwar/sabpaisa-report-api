"""
URL patterns for reports app
"""
from django.urls import path
from .views import (
    ReportGenerateView,
    ReportDownloadView,
    ReportStatusView,
    ReportListView
)

app_name = 'reports'

urlpatterns = [
    # Report generation
    path('generate/', ReportGenerateView.as_view(), name='report-generate'),

    # Report management
    path('list/', ReportListView.as_view(), name='report-list'),
    path('status/<str:task_id>/', ReportStatusView.as_view(), name='report-status'),
    path('download/<str:task_id>/', ReportDownloadView.as_view(), name='report-download'),
]