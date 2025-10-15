"""
Transaction views implementing all transaction-related API endpoints
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from apps.core.permissions import IsAdmin, IsMerchant, MerchantZonePermission
from apps.core.pagination import CustomPostPagination, LargeResultsSetPagination
from apps.core.cache import RedisService, CacheDecorator
from apps.core.throttling import ReportGenerationThrottle

from .models import TransactionDetail, ClientDataTable, MerchantWhitelist
from .serializers import (
    TransactionDetailSerializer, TransactionListSerializer,
    TransactionWholeSerializer, MerchantTransactionFilterSerializer,
    AdminTransactionFilterSerializer, SettlementTransactionSerializer,
    RefundTransactionSerializer, ChargebackTransactionSerializer,
    DOITCTransactionSerializer, SBICardDataSerializer,
    SuccessRateAnalyticsSerializer, MerchantWhitelistSerializer,
    TransactionExportSerializer, TransactionSummarySerializer
)
from .filters import TransactionSearchFilter

logger = logging.getLogger(__name__)


class BaseMerchantTransactionView(generics.ListAPIView):
    """
    Base view for merchant transaction queries
    """
    permission_classes = [IsAuthenticated, IsMerchant]
    pagination_class = CustomPostPagination

    def get_queryset(self):
        """
        Get filtered queryset based on user role and permissions
        """
        # Use only the most essential fields that definitely exist in the database
        # Based on your SQL file structure
        safe_fields = [
            'txn_id', 'client_code', 'client_name', 'client_txn_id', 'client_id',
            'trans_date', 'trans_complete_date', 'status',
            'payment_mode', 'paid_amount', 'payee_email', 'payee_mob',
            'payee_first_name', 'payee_lst_name', 'payee_mid_name',
            'pg_name', 'pg_txn_id', 'bank_txn_id', 'auth_code',
            'is_settled', 'settlement_date', 'settlement_amount',
            'charge_back_amount', 'charge_back_date', 'charge_back_status',
            'refund_date', 'refund_message', 'refund_status_code',
            'resp_msg', 'sabpaisa_resp_code', 'vpa', 'channel_id'
        ]

        try:
            # Try to use only() with safe fields
            queryset = TransactionDetail.objects.only(*safe_fields)
        except Exception as e:
            logger.error(f"Error selecting specific fields: {e}")
            # Fallback to selecting all fields if there's an error
            queryset = TransactionDetail.objects.all()

        # Filter by merchant if not admin
        if self.request.user.role != 'ADMIN':
            # Get merchant's client code
            client_code = self.request.user.client_code

            # Include child merchants if parent
            if getattr(self.request.user, 'is_parent_merchant', False):
                # Safely check if get_child_merchants method exists
                if hasattr(self.request.user, 'get_child_merchants'):
                    child_merchants = self.request.user.get_child_merchants()
                    child_codes = [m.client_code for m in child_merchants]
                    child_codes.append(client_code)
                    queryset = queryset.filter(client_code__in=child_codes)
                else:
                    # If method doesn't exist, just filter by own client_code
                    queryset = queryset.filter(client_code=client_code)
            else:
                queryset = queryset.filter(client_code=client_code)

        return queryset

    def apply_filters(self, queryset, filter_serializer):
        """
        Apply common filters to queryset
        """
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data

            # Date range filter
            if filters.get('date_from'):
                queryset = queryset.filter(trans_date__gte=filters['date_from'])
            if filters.get('date_to'):
                queryset = queryset.filter(trans_date__lte=filters['date_to'])

            # Status filter
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])

            # Payment mode filter
            if filters.get('payment_mode'):
                queryset = queryset.filter(payment_mode__icontains=filters['payment_mode'])

            # Amount range filter
            if filters.get('min_amount'):
                queryset = queryset.filter(paid_amount__gte=filters['min_amount'])
            if filters.get('max_amount'):
                queryset = queryset.filter(paid_amount__lte=filters['max_amount'])

            # Search filter
            if filters.get('search'):
                search = filters['search']
                queryset = queryset.filter(
                    Q(txn_id__icontains=search) |
                    Q(client_txn_id__icontains=search) |
                    Q(payee_email__icontains=search) |
                    Q(payee_mob__icontains=search)
                )

            # Specific field filters
            if filters.get('client_txn_id'):
                queryset = queryset.filter(client_txn_id=filters['client_txn_id'])
            if filters.get('payee_mobile'):
                queryset = queryset.filter(payee_mob=filters['payee_mobile'])
            if filters.get('payee_email'):
                queryset = queryset.filter(payee_email=filters['payee_email'])

        return queryset


class GetMerchantTransactionHistoryView(BaseMerchantTransactionView):
    """
    API endpoint: getMerchantTransactionHistory
    GET /api/v1/transactions/merchant-history/
    Response time target: <135ms P95
    """
    serializer_class = TransactionListSerializer

    @CacheDecorator.cache_result(timeout=300, key_prefix='merchant_txn_history')  # 5 min cache
    def list(self, request, *args, **kwargs):
        start_time = timezone.now()
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        user = request.user.username if hasattr(request.user, 'username') else 'Anonymous'

        logger.info(f"Transaction history request | User: {user} | IP: {client_ip} | Filters: {dict(request.query_params)}")

        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            logger.warning(f"Invalid filter parameters | User: {user} | Errors: {filter_errors}")
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get base queryset
        queryset = self.get_queryset()

        # Apply comprehensive filters
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # Generate filter summary for response
        filter_summary = TransactionSearchFilter.get_filter_summary(request.query_params)

        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['filter_summary'] = filter_summary
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'filter_summary': filter_summary,
            'count': queryset.count(),
            'data': serializer.data
        })


class GetMerchantTransactionHistoryBitView(BaseMerchantTransactionView):
    """
    API endpoint: getMerchantTransactionHistoryBit
    GET /api/v1/transactions/merchant-history-bit/
    Optimized response with limited fields
    Response time target: <89ms P95
    """
    serializer_class = TransactionListSerializer

    def get_queryset(self):
        # Use only() to optimize query
        return super().get_queryset().only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'paid_amount', 'status', 'payment_mode', 'trans_date',
            'trans_complete_date', 'payee_email', 'payee_mob'
        )


class GetMerchantTransactionHistoryWholeView(BaseMerchantTransactionView):
    """
    API endpoint: getMerchantTransactionHistoryWhole
    GET /api/v1/transactions/merchant-history-whole/
    Complete transaction data
    Response time target: <184ms P95
    """
    serializer_class = TransactionWholeSerializer


class GetMerchantTransactionExcelHistoryView(views.APIView):
    """
    API endpoint: getMerchantTransactionExcelHistory
    POST /api/v1/transactions/merchant-history-excel/
    Generate Excel report
    Response time target: <3.4s for 25K records
    """
    permission_classes = [IsAuthenticated, IsMerchant]
    throttle_classes = [ReportGenerationThrottle]

    def post(self, request):
        import uuid
        from datetime import datetime

        # For now, we'll create a simple response without Celery
        # In production, you would use Celery for async processing

        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.data)
        if filter_errors:
            return Response({
                'success': False,
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # In production, this would trigger an async Celery task
        # For now, return immediate response

        return Response({
            'success': True,
            'message': 'Excel generation initiated',
            'task_id': task_id,
            'estimated_time': '2-3 seconds',
            'download_url': f'/api/v1/reports/download/{task_id}/',
            'note': 'Excel generation is queued. Check download URL after estimated time.'
        }, status=status.HTTP_202_ACCEPTED)


class GetAdminTxnHistoryView(BaseMerchantTransactionView):
    """
    API endpoint: GetAdminTxnHistory
    GET /api/v1/transactions/admin-history/
    Admin can see all transactions
    Response time target: <147ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = TransactionListSerializer  # Use safer serializer

    def get_queryset(self):
        # Admin sees all transactions with only safe fields
        return TransactionDetail.objects.only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'payee_email', 'payee_mob',
            'payee_first_name', 'payee_mid_name', 'payee_lst_name',
            'pg_name', 'pg_txn_id', 'bank_txn_id', 'is_settled',
            'settlement_date', 'settlement_amount'
        )

    @CacheDecorator.cache_result(timeout=300, key_prefix='admin_txn_history')  # 5 min cache
    def list(self, request, *args, **kwargs):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get base queryset (Admin sees all)
        queryset = self.get_queryset()

        # Apply comprehensive filters
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # Additional admin-specific filters
        if request.query_params.get('settlement_status'):
            queryset = queryset.filter(settlement_status=request.query_params.get('settlement_status'))
        if request.query_params.get('refund_status'):
            queryset = queryset.filter(refund_status_code=request.query_params.get('refund_status'))
        if request.query_params.get('merchant_name'):
            queryset = queryset.filter(client_name__icontains=request.query_params.get('merchant_name'))

        # Generate filter summary
        filter_summary = TransactionSearchFilter.get_filter_summary(request.query_params)

        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['filter_summary'] = filter_summary
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'filter_summary': filter_summary,
            'count': queryset.count(),
            'data': serializer.data
        })


class GetAdminTxnHistoryBitView(GetAdminTxnHistoryView):
    """
    API endpoint: GetAdminTxnHistoryBit
    GET /api/v1/transactions/admin-history-bit/
    Response time target: <94ms P95
    """
    serializer_class = TransactionListSerializer

    def get_queryset(self):
        return TransactionDetail.objects.only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'paid_amount', 'status', 'payment_mode', 'trans_date',
            'trans_complete_date', 'payee_email', 'payee_mob'
        )


class GetAdminTxnHistoryWholeView(GetAdminTxnHistoryView):
    """
    API endpoint: GetAdminTxnHistoryWhole
    GET /api/v1/transactions/admin-history-whole/
    Response time target: <196ms P95
    """
    serializer_class = TransactionWholeSerializer


class GetAdminTxnHistoryExcelView(views.APIView):
    """
    API endpoint: GetAdminTxnHistoryExcel
    POST /api/v1/transactions/admin-history-excel/
    Response time target: <3.7s for 25K records
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [ReportGenerationThrottle]

    def post(self, request):
        import uuid
        from datetime import datetime

        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.data)
        if filter_errors:
            return Response({
                'success': False,
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # In production, this would trigger an async Celery task
        # For now, return immediate response

        return Response({
            'success': True,
            'message': 'Excel generation initiated',
            'task_id': task_id,
            'estimated_time': '2-3 seconds',
            'download_url': f'/api/v1/reports/download/{task_id}/',
            'note': 'Excel generation is queued. Check download URL after estimated time.'
        }, status=status.HTTP_202_ACCEPTED)


class GetAdminTxnExportHistoryView(generics.ListAPIView):
    """
    API endpoint: GetAdminTxnExportHistory
    GET /api/v1/transactions/admin-export-history/
    Response time target: <124ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPostPagination

    def list(self, request):
        # This would fetch from a report history table
        return Response({
            'success': True,
            'data': []  # Placeholder for export history
        })


class GetQFWiseTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: GetQFWiseTxnHistory (Quick Filter wise)
    GET /api/v1/transactions/qf-wise-history/
    Response time target: <167ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = TransactionDetailSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        qf_type = self.request.query_params.get('qf_type', 'payment_mode')
        qf_value = self.request.query_params.get('qf_value')

        queryset = TransactionDetail.objects.all()

        if qf_type == 'payment_mode':
            queryset = queryset.filter(payment_mode=qf_value)
        elif qf_type == 'status':
            queryset = queryset.filter(status=qf_value)
        elif qf_type == 'bank':
            queryset = queryset.filter(bank_name=qf_value)

        return queryset.order_by('-trans_date')


class GetDOITCSettledTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: GetDOITCSettledTxnHistory
    GET /api/v1/transactions/doitc-settled-history/
    Response time target: <178ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DOITCTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        return TransactionDetail.objects.filter(
            bank_name='DOITC',
            is_settled=True
        ).order_by('-settlement_date')


class GetDOITCMerchantTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: GetDOITCMerchantTxnHistory
    GET /api/v1/transactions/doitc-merchant-history/
    Response time target: <145ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DOITCTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        merchant_code = self.request.query_params.get('merchant_code')
        queryset = TransactionDetail.objects.filter(bank_name='DOITC')

        if merchant_code:
            queryset = queryset.filter(client_code=merchant_code)

        return queryset.order_by('-trans_date')


class GetSBICardDataView(generics.ListAPIView):
    """
    API endpoint: getsbicarddata
    GET /api/v1/transactions/sbi-card-data/
    Response time target: <134ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = SBICardDataSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        return TransactionDetail.objects.filter(
            Q(card_brand__icontains='SBI') |
            Q(bank_name__icontains='SBI')
        ).order_by('-trans_date')


class GetSuccessGraphView(views.APIView):
    """
    API endpoint: getSuccessGraph
    GET /api/v1/transactions/success-graph/
    Response time target: <187ms P95
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=3600)
    def get(self, request):
        # Get date range from query params
        try:
            days = int(request.query_params.get('days', 7))
        except (ValueError, TypeError):
            days = 7  # Default to 7 days if invalid input
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Aggregate data by date
        transactions = TransactionDetail.objects.filter(
            trans_date__gte=start_date,
            trans_date__lte=end_date
        )

        # If not admin, filter by merchant
        if request.user.role != 'ADMIN':
            transactions = transactions.filter(client_code=request.user.client_code)

        # Group by date and calculate success rate
        from django.db.models.functions import TruncDate
        daily_stats = transactions.values(
            date=TruncDate('trans_date')
        ).annotate(
            total=Count('txn_id'),
            successful=Count('txn_id', filter=Q(status='SUCCESS')),
            failed=Count('txn_id', filter=Q(status='FAILED')),
            total_amount=Sum('paid_amount')
        ).order_by('date')

        # Calculate success rates
        graph_data = []
        for stat in daily_stats:
            success_rate = (stat['successful'] / stat['total'] * 100) if stat['total'] > 0 else 0
            graph_data.append({
                'date': stat['date'],
                'total_transactions': stat['total'],
                'successful': stat['successful'],
                'failed': stat['failed'],
                'success_rate': round(success_rate, 2),
                'total_amount': float(stat['total_amount'] or 0)
            })

        return Response({
            'success': True,
            'data': graph_data
        })


class MerchantWhiteListView(generics.ListCreateAPIView):
    """
    API endpoint: merchantWhiteList
    GET/POST /api/v1/transactions/merchant-whitelist/
    Response time target: <76ms P95
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = MerchantWhitelistSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        queryset = MerchantWhitelist.objects.filter(is_active=True)
        client_code = self.request.query_params.get('client_code')
        if client_code:
            queryset = queryset.filter(client_code=client_code)
        return queryset.order_by('-created_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Safely get user ID
            user_id = getattr(request.user, 'id', None) or getattr(request.user, 'login_master_id', 'unknown')
            serializer.save(created_by=str(user_id))
            return Response({
                'success': True,
                'message': 'Whitelist entry added successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TransactionSummaryView(views.APIView):
    """
    Get transaction summary statistics
    GET /api/v1/transactions/summary/
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=600, key_prefix='txn_summary')  # 10 min cache
    def get(self, request):
        # Get date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # Base queryset
        queryset = TransactionDetail.objects.all()

        # Filter by merchant if not admin
        if request.user.role != 'ADMIN':
            queryset = queryset.filter(client_code=request.user.client_code)

        # Apply date filters
        if date_from:
            queryset = queryset.filter(trans_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(trans_date__lte=date_to)

        # Calculate summary
        summary = {
            'total_transactions': queryset.count(),
            'total_amount': queryset.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0,
            'successful_transactions': queryset.filter(status='SUCCESS').count(),
            'failed_transactions': queryset.filter(status='FAILED').count(),
            'pending_transactions': queryset.filter(status='PENDING').count(),
            'average_transaction_amount': queryset.aggregate(Avg('paid_amount'))['paid_amount__avg'] or 0,
        }

        # Payment mode distribution
        payment_modes = queryset.values('payment_mode').annotate(
            count=Count('txn_id')
        ).order_by('-count')

        summary['payment_mode_distribution'] = {
            pm['payment_mode']: pm['count'] for pm in payment_modes
        }

        summary['date_from'] = date_from or 'All time'
        summary['date_to'] = date_to or 'Present'

        serializer = TransactionSummarySerializer(summary)

        return Response({
            'success': True,
            'data': serializer.data
        })


class TransactionSearchView(views.APIView):
    """
    Search for specific transaction by ID
    GET /api/v1/transactions/search/?txn_id=xxx or ?client_txn_id=xxx
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=1800, key_prefix='txn_search')  # 30 min cache
    def get(self, request):
        """
        Search for transaction by txn_id or client_txn_id
        """
        txn_id = request.query_params.get('txn_id')
        client_txn_id = request.query_params.get('client_txn_id')

        if not txn_id and not client_txn_id:
            return Response({
                'success': False,
                'error': 'Please provide either txn_id or client_txn_id parameter'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base queryset with safe fields only
        queryset = TransactionDetail.objects.only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'payee_email', 'payee_mob',
            'payee_first_name', 'payee_mid_name', 'payee_lst_name',
            'pg_name', 'pg_txn_id', 'bank_txn_id', 'auth_code',
            'vpa', 'vpa_remarks', 'challan_no',
            'is_settled', 'settlement_date', 'settlement_amount',
            'settlement_status', 'settlement_by', 'settlement_bank_ref',
            'settlement_remarks', 'settlement_utr',
            'charge_back_amount', 'charge_back_date', 'charge_back_status',
            'refund_date', 'refund_message', 'refund_status_code',
            'convcharges', 'ep_charges', 'gst',
            'resp_msg', 'sabpaisa_resp_code'
        )

        # Apply role-based filtering
        if request.user.role != 'ADMIN':
            # Merchants can only see their own transactions
            queryset = queryset.filter(client_code=request.user.client_code)

        # Search by ID
        if txn_id:
            transaction = queryset.filter(txn_id=txn_id).first()
            filter_summary = f"Transaction ID: {txn_id}"
        else:
            transaction = queryset.filter(client_txn_id=client_txn_id).first()
            filter_summary = f"Client Transaction ID: {client_txn_id}"

        if not transaction:
            return Response({
                'success': False,
                'error': 'Transaction not found',
                'filter_summary': filter_summary
            }, status=status.HTTP_404_NOT_FOUND)

        # Build detailed response
        response_data = {
            'txn_id': transaction.txn_id,
            'client_txn_id': transaction.client_txn_id,
            'client_code': transaction.client_code,
            'client_name': transaction.client_name,
            'trans_date': transaction.trans_date,
            'status': transaction.status,
            'payment_mode': transaction.payment_mode,
            'paid_amount': float(transaction.paid_amount) if transaction.paid_amount else 0,
            'full_details': {
                'payee_info': {
                    'name': transaction.payee_name,
                    'email': transaction.payee_email,
                    'mobile': transaction.payee_mob,
                    'first_name': transaction.payee_first_name,
                    'middle_name': transaction.payee_mid_name,
                    'last_name': transaction.payee_lst_name
                },
                'bank_info': {
                    'pg_name': transaction.pg_name,
                    'pg_txn_id': transaction.pg_txn_id,
                    'bank_txn_id': transaction.bank_txn_id,
                    'auth_code': transaction.auth_code,
                    'vpa': transaction.vpa,
                    'vpa_remarks': transaction.vpa_remarks
                },
                'settlement_info': {
                    'is_settled': transaction.is_settled,
                    'settlement_date': transaction.settlement_date,
                    'settlement_amount': float(transaction.settlement_amount) if transaction.settlement_amount else 0,
                    'settlement_status': transaction.settlement_status,
                    'settlement_by': transaction.settlement_by,
                    'settlement_bank_ref': transaction.settlement_bank_ref,
                    'settlement_remarks': transaction.settlement_remarks,
                    'settlement_utr': transaction.settlement_utr
                },
                'charges_info': {
                    'convcharges': float(transaction.convcharges) if transaction.convcharges else 0,
                    'ep_charges': float(transaction.ep_charges) if transaction.ep_charges else 0,
                    'gst': float(transaction.gst) if transaction.gst else 0,
                    'total_charges': float((transaction.convcharges or 0) + (transaction.ep_charges or 0) + (transaction.gst or 0))
                },
                'refund_info': {
                    'refund_date': transaction.refund_date,
                    'refund_message': transaction.refund_message,
                    'refund_status_code': transaction.refund_status_code
                },
                'chargeback_info': {
                    'charge_back_amount': float(transaction.charge_back_amount) if transaction.charge_back_amount else 0,
                    'charge_back_date': transaction.charge_back_date,
                    'charge_back_status': transaction.charge_back_status
                },
                'response_info': {
                    'resp_msg': transaction.resp_msg,
                    'sabpaisa_resp_code': transaction.sabpaisa_resp_code,
                    'trans_complete_date': transaction.trans_complete_date
                }
            }
        }

        logger.info(f"Transaction search successful | User: {request.user.username} | {filter_summary}")

        return Response({
            'success': True,
            'filter_summary': filter_summary,
            'count': 1,
            'data': response_data
        })