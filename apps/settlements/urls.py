"""
URL patterns for settlements app
"""
from django.urls import path
from .views import (
    GetSettledTxnHistoryView,
    GetSettledTxnExcelHistoryView,
    GetSettledTxnExcelV2HistoryView,
    SettledGroupedView,
    QfWiseSettledTxnHistoryView,
    GetRefundTxnHistoryView,
    GetMerchantRefundHistoryView,
    GetChargebackTxnHistoryView,
    ReconciliationView
)

app_name = 'settlements'

urlpatterns = [
    # Settlement APIs (5 endpoints)
    path('settled-history/', GetSettledTxnHistoryView.as_view(), name='settled-history'),
    path('settled-excel/', GetSettledTxnExcelHistoryView.as_view(), name='settled-excel'),
    path('settled-excel-v2/', GetSettledTxnExcelV2HistoryView.as_view(), name='settled-excel-v2'),
    path('grouped-view/', SettledGroupedView.as_view(), name='grouped-view'),
    path('qf-wise-settled/', QfWiseSettledTxnHistoryView.as_view(), name='qf-wise-settled'),

    # Financial Management APIs (3 endpoints)
    path('refund-history/', GetRefundTxnHistoryView.as_view(), name='refund-history'),
    path('merchant-refund-history/', GetMerchantRefundHistoryView.as_view(), name='merchant-refund-history'),
    path('chargeback-history/', GetChargebackTxnHistoryView.as_view(), name='chargeback-history'),

    # Reconciliation
    path('reconciliation/', ReconciliationView.as_view(), name='reconciliation'),
]