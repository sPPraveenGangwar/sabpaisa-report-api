"""
QwikForms URL Configuration
All routes require Admin authentication
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QwikFormsTransactionViewSet,
    QwikFormsSettlementViewSet,
    QwikFormsAnalyticsViewSet,
    QwikFormsReportViewSet
)

# Create router
router = DefaultRouter()
router.register(r'transactions', QwikFormsTransactionViewSet, basename='qwikforms-transactions')
router.register(r'settlements', QwikFormsSettlementViewSet, basename='qwikforms-settlements')
router.register(r'analytics', QwikFormsAnalyticsViewSet, basename='qwikforms-analytics')
router.register(r'reports', QwikFormsReportViewSet, basename='qwikforms-reports')

app_name = 'qwikforms'

urlpatterns = [
    path('', include(router.urls)),
]