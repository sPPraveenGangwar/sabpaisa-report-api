"""
Analytics module URL patterns
"""
from django.urls import path
from .views import (
    MerchantAnalyticsView,
    PaymentModeAnalyticsView,
    SettlementAnalyticsView,
    RefundChargebackAnalyticsView,
    ComparativeAnalyticsView,
    ExecutiveDashboardView
)

app_name = 'analytics'

urlpatterns = [
    # Analytics endpoints
    path('merchant-analytics/', MerchantAnalyticsView.as_view(), name='merchant-analytics'),
    path('payment-mode-analytics/', PaymentModeAnalyticsView.as_view(), name='payment-mode-analytics'),
    path('settlement-analytics/', SettlementAnalyticsView.as_view(), name='settlement-analytics'),
    path('refund-chargeback/', RefundChargebackAnalyticsView.as_view(), name='refund-chargeback'),
    path('comparative/', ComparativeAnalyticsView.as_view(), name='comparative'),
    path('executive-dashboard/', ExecutiveDashboardView.as_view(), name='executive-dashboard'),
]