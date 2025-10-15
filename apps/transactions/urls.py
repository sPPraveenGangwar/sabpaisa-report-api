"""
URL patterns for transaction app
"""
from django.urls import path
from .views import (
    GetMerchantTransactionHistoryView,
    GetMerchantTransactionHistoryBitView,
    GetMerchantTransactionHistoryWholeView,
    GetMerchantTransactionExcelHistoryView,
    GetAdminTxnHistoryView,
    GetAdminTxnHistoryBitView,
    GetAdminTxnHistoryWholeView,
    GetAdminTxnHistoryExcelView,
    GetAdminTxnExportHistoryView,
    GetQFWiseTxnHistoryView,
    GetDOITCSettledTxnHistoryView,
    GetDOITCMerchantTxnHistoryView,
    GetSBICardDataView,
    GetSuccessGraphView,
    MerchantWhiteListView,
    TransactionSummaryView,
    TransactionSearchView
)

app_name = 'transactions'

urlpatterns = [
    # Merchant Transaction APIs (4 endpoints)
    path('merchant-history/', GetMerchantTransactionHistoryView.as_view(), name='merchant-history'),
    path('merchant-history-bit/', GetMerchantTransactionHistoryBitView.as_view(), name='merchant-history-bit'),
    path('merchant-history-whole/', GetMerchantTransactionHistoryWholeView.as_view(), name='merchant-history-whole'),
    path('merchant-history-excel/', GetMerchantTransactionExcelHistoryView.as_view(), name='merchant-history-excel'),

    # Admin Transaction APIs (6 endpoints)
    path('admin-history/', GetAdminTxnHistoryView.as_view(), name='admin-history'),
    path('admin-history-bit/', GetAdminTxnHistoryBitView.as_view(), name='admin-history-bit'),
    path('admin-history-whole/', GetAdminTxnHistoryWholeView.as_view(), name='admin-history-whole'),
    path('admin-history-excel/', GetAdminTxnHistoryExcelView.as_view(), name='admin-history-excel'),
    path('admin-export-history/', GetAdminTxnExportHistoryView.as_view(), name='admin-export-history'),
    path('qf-wise-history/', GetQFWiseTxnHistoryView.as_view(), name='qf-wise-history'),

    # Bank Integration APIs (3 endpoints)
    path('doitc-settled-history/', GetDOITCSettledTxnHistoryView.as_view(), name='doitc-settled-history'),
    path('doitc-merchant-history/', GetDOITCMerchantTxnHistoryView.as_view(), name='doitc-merchant-history'),
    path('sbi-card-data/', GetSBICardDataView.as_view(), name='sbi-card-data'),

    # Analytics APIs (2 endpoints)
    path('success-graph/', GetSuccessGraphView.as_view(), name='success-graph'),
    path('merchant-whitelist/', MerchantWhiteListView.as_view(), name='merchant-whitelist'),

    # Summary endpoint
    path('summary/', TransactionSummaryView.as_view(), name='transaction-summary'),

    # Search endpoint
    path('search/', TransactionSearchView.as_view(), name='transaction-search'),
]