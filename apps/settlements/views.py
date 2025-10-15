"""
Settlement views for settlement processing APIs
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, F, Value, FloatField, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta

from apps.core.permissions import IsAdmin, IsMerchant
from apps.core.pagination import CustomPostPagination
from apps.core.throttling import ReportGenerationThrottle
from apps.core.cache import CacheDecorator
from apps.transactions.models import TransactionDetail
from apps.transactions.serializers import (
    SettlementTransactionSerializer,
    RefundTransactionSerializer,
    ChargebackTransactionSerializer
)
from apps.transactions.filters import TransactionSearchFilter


class GetSettledTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: GetSettledTxnHistory
    GET /api/v1/settlements/settled-history/
    Response time target: <156ms P95
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SettlementTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        # Start with settled transactions, using only safe fields
        queryset = TransactionDetail.objects.filter(is_settled=True).only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'payee_email', 'payee_mob',
            'payee_first_name', 'payee_mid_name', 'payee_lst_name',
            'pg_name', 'pg_txn_id', 'bank_txn_id',
            'is_settled', 'settlement_date', 'settlement_amount',
            'settlement_status', 'settlement_by', 'settlement_bank_ref',
            'settlement_remarks', 'settlement_utr',
            'convcharges', 'ep_charges', 'gst'
        )
        return queryset

    @CacheDecorator.cache_result(timeout=300, key_prefix='settled_txn_history')  # 5 min cache
    def list(self, request, *args, **kwargs):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get base queryset
        queryset = self.get_queryset()

        # Apply comprehensive filters (includes date, merchant, payment mode, status, amount)
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # Settlement-specific filters
        settlement_status = request.query_params.get('settlement_status')
        if settlement_status:
            # Map COMPLETED status to include both COMPLETED and SETTLED in DB
            # This handles variations in DB values (COMPLETED/SETTLED/Completed/Settled)
            if settlement_status.upper() in ['COMPLETED', 'SETTLED']:
                queryset = queryset.filter(
                    Q(settlement_status__iexact='COMPLETED') |
                    Q(settlement_status__iexact='SETTLED')
                )
            else:
                queryset = queryset.filter(settlement_status=settlement_status)

        settlement_utr = request.query_params.get('settlement_utr')
        if settlement_utr:
            queryset = queryset.filter(settlement_utr=settlement_utr)

        # Use settlement_date for date filters if specified
        use_settlement_date = request.query_params.get('use_settlement_date', 'false').lower() == 'true'
        if use_settlement_date:
            date_filter = request.query_params.get('date_filter', 'custom')
            if date_filter != 'custom':
                date_from, date_to = TransactionSearchFilter.get_date_range(date_filter)
                if date_from and date_to:
                    queryset = queryset.filter(settlement_date__range=[date_from, date_to])
            else:
                date_from = request.query_params.get('date_from')
                date_to = request.query_params.get('date_to')
                if date_from:
                    queryset = queryset.filter(settlement_date__gte=date_from)
                if date_to:
                    queryset = queryset.filter(settlement_date__lte=date_to)

        # Order by settlement date
        queryset = queryset.order_by('-settlement_date')

        # Generate filter summary
        filter_summary = TransactionSearchFilter.get_filter_summary(request.query_params)
        if settlement_status:
            if settlement_status.upper() in ['COMPLETED', 'SETTLED']:
                filter_summary += f" | Settlement Status: {settlement_status} (includes both COMPLETED and SETTLED)"
            else:
                filter_summary += f" | Settlement Status: {settlement_status}"

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


class GetSettledTxnExcelHistoryView(views.APIView):
    """
    API endpoint: GetSettledTxnExcelHistory
    POST /api/v1/settlements/settled-excel/
    Response time target: <2.9s for 15K records
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReportGenerationThrottle]

    def post(self, request):
        from apps.reports.tasks import generate_settlement_excel

        # Safely get user ID
        user_id = getattr(request.user, 'id', None) or getattr(request.user, 'login_master_id', None)

        task = generate_settlement_excel.delay(
            user_id=user_id,
            filters=request.data
        )

        return Response({
            'success': True,
            'message': 'Settlement Excel generation initiated',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class GetSettledTxnExcelV2HistoryView(views.APIView):
    """
    API endpoint: GetSettledTxnExcelV2History
    POST /api/v1/settlements/settled-excel-v2/
    Enhanced version with more features
    Response time target: <3.2s
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReportGenerationThrottle]

    def post(self, request):
        from apps.reports.tasks import generate_settlement_excel_v2

        # Safely get user ID
        user_id = getattr(request.user, 'id', None) or getattr(request.user, 'login_master_id', None)

        task = generate_settlement_excel_v2.delay(
            user_id=user_id,
            filters=request.data,
            include_charts=True
        )

        return Response({
            'success': True,
            'message': 'Enhanced Settlement Excel generation initiated',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class SettledGroupedView(generics.ListAPIView):
    """
    API endpoint: SettledGroupedView
    GET /api/v1/settlements/grouped-view/
    Response time target: <203ms P95
    """
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPostPagination

    @CacheDecorator.cache_result(timeout=600, key_prefix='settled_grouped')  # 10 min cache
    def list(self, request):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Start with settled transactions, using only safe fields
        queryset = TransactionDetail.objects.filter(is_settled=True).only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'is_settled', 'settlement_date', 'settlement_amount',
            'settlement_status', 'settlement_by', 'settlement_bank_ref',
            'settlement_remarks', 'settlement_utr',
            'convcharges', 'ep_charges', 'gst'
        )

        # Apply comprehensive filters
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # Use settlement_date for date filters if specified
        use_settlement_date = request.query_params.get('use_settlement_date', 'false').lower() == 'true'
        if use_settlement_date:
            date_filter = request.query_params.get('date_filter', 'custom')
            if date_filter != 'custom':
                date_from, date_to = TransactionSearchFilter.get_date_range(date_filter)
                if date_from and date_to:
                    queryset = queryset.filter(settlement_date__range=[date_from, date_to])
            else:
                date_from = request.query_params.get('date_from')
                date_to = request.query_params.get('date_to')
                if date_from:
                    queryset = queryset.filter(settlement_date__gte=date_from)
                if date_to:
                    queryset = queryset.filter(settlement_date__lte=date_to)

        group_by = request.query_params.get('group_by', 'date')

        # Group data
        if group_by == 'date':
            from django.db.models.functions import TruncDate
            grouped_data = queryset.values(
                date=TruncDate('settlement_date')
            ).annotate(
                total_count=Count('txn_id'),
                total_amount=Sum('settlement_amount'),
                # Calculate effective amount as settlement_amount minus charges
                total_effective=Sum(
                    Coalesce(F('settlement_amount'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('convcharges'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('ep_charges'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('gst'), Value(0.0, output_field=FloatField())),
                    output_field=FloatField()
                )
            ).order_by('-date')
        elif group_by == 'merchant':
            grouped_data = queryset.values('client_code', 'client_name').annotate(
                total_count=Count('txn_id'),
                total_amount=Sum('settlement_amount'),
                total_effective=Sum(
                    Coalesce(F('settlement_amount'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('convcharges'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('ep_charges'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('gst'), Value(0.0, output_field=FloatField())),
                    output_field=FloatField()
                )
            ).order_by('-total_amount')
        else:
            grouped_data = queryset.values('settlement_status').annotate(
                total_count=Count('txn_id'),
                total_amount=Sum('settlement_amount'),
                total_effective=Sum(
                    Coalesce(F('settlement_amount'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('convcharges'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('ep_charges'), Value(0.0, output_field=FloatField())) -
                    Coalesce(F('gst'), Value(0.0, output_field=FloatField())),
                    output_field=FloatField()
                )
            ).order_by('-total_amount')

        return Response({
            'success': True,
            'data': list(grouped_data)
        })


class QfWiseSettledTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: qfWiseSettledTxnHistory
    GET /api/v1/settlements/qf-wise-settled/
    Response time target: <167ms P95
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SettlementTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        queryset = TransactionDetail.objects.filter(is_settled=True).only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'is_settled', 'settlement_date', 'settlement_amount',
            'settlement_status', 'settlement_by', 'settlement_bank_ref',
            'settlement_remarks', 'settlement_utr',
            'convcharges', 'ep_charges', 'gst'
        )
        return queryset

    @CacheDecorator.cache_result(timeout=300, key_prefix='qf_settled')  # 5 min cache
    def list(self, request, *args, **kwargs):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
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

        # QF specific filters
        qf_type = request.query_params.get('qf_type', 'payment_mode')
        qf_value = request.query_params.get('qf_value')

        if qf_value:
            if qf_type == 'payment_mode':
                queryset = queryset.filter(payment_mode=qf_value)
            elif qf_type == 'bank':
                queryset = queryset.filter(bank_name=qf_value)
            elif qf_type == 'utr':
                queryset = queryset.filter(settlement_utr=qf_value)

        # Order by settlement date
        queryset = queryset.order_by('-settlement_date')

        # Generate filter summary
        filter_summary = TransactionSearchFilter.get_filter_summary(request.query_params)
        if qf_value:
            filter_summary += f" | {qf_type.replace('_', ' ').title()}: {qf_value}"

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


class GetRefundTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: GetRefundTxnHistory
    GET /api/v1/settlements/refund-history/
    Response time target: <142ms P95
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RefundTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        # Get refunded transactions with safe fields
        queryset = TransactionDetail.objects.filter(
            Q(refund_date__isnull=False) |
            Q(refund_status_code__isnull=False)
        ).only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'status', 'payment_mode', 'paid_amount',
            'payee_first_name', 'payee_mid_name', 'payee_lst_name',
            'refund_date', 'refunded_date',
            'refund_message', 'refund_status_code',
            'refund_request_from', 'pg_name', 'bank_txn_id'
        )
        return queryset

    @CacheDecorator.cache_result(timeout=300, key_prefix='refund_history')  # 5 min cache
    def list(self, request, *args, **kwargs):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
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

        # Refund-specific filters
        refund_status = request.query_params.get('refund_status')
        if refund_status:
            queryset = queryset.filter(refund_status_code=refund_status)

        # Use refund_message as a proxy for refund_reason since refund_reason doesn't exist
        refund_reason = request.query_params.get('refund_reason')
        if refund_reason:
            # Filter by refund_message or refund_request_from
            queryset = queryset.filter(
                Q(refund_message__icontains=refund_reason) |
                Q(refund_request_from__icontains=refund_reason)
            )

        # Use refund_date for date filters if specified
        use_refund_date = request.query_params.get('use_refund_date', 'false').lower() == 'true'
        if use_refund_date:
            date_filter = request.query_params.get('date_filter', 'custom')
            if date_filter != 'custom':
                date_from, date_to = TransactionSearchFilter.get_date_range(date_filter)
                if date_from and date_to:
                    queryset = queryset.filter(refund_date__range=[date_from, date_to])
            else:
                date_from = request.query_params.get('date_from')
                date_to = request.query_params.get('date_to')
                if date_from:
                    queryset = queryset.filter(refund_date__gte=date_from)
                if date_to:
                    queryset = queryset.filter(refund_date__lte=date_to)

        # Refund amount filters - use paid_amount as proxy since refund_amount doesn't exist
        min_refund_amount = request.query_params.get('min_refund_amount')
        max_refund_amount = request.query_params.get('max_refund_amount')
        if min_refund_amount:
            try:
                queryset = queryset.filter(paid_amount__gte=float(min_refund_amount))
            except (ValueError, TypeError):
                pass
        if max_refund_amount:
            try:
                queryset = queryset.filter(paid_amount__lte=float(max_refund_amount))
            except (ValueError, TypeError):
                pass

        # Order by refund date
        queryset = queryset.order_by('-refund_date', '-trans_date')

        # Generate filter summary
        filter_summary = TransactionSearchFilter.get_filter_summary(request.query_params)
        if refund_status:
            filter_summary += f" | Refund Status: {refund_status}"
        if refund_reason:
            filter_summary += f" | Refund Reason: {refund_reason}"

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


class GetMerchantRefundHistoryView(generics.ListAPIView):
    """
    API endpoint: GetMerchantRefundHistory
    GET /api/v1/settlements/merchant-refund-history/
    Returns refund transactions for a specific merchant
    Response time target: <150ms P95
    """
    permission_classes = [IsAuthenticated, IsMerchant]
    serializer_class = RefundTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        # Get refunded transactions for the merchant with safe fields
        queryset = TransactionDetail.objects.filter(
            Q(refund_date__isnull=False) |
            Q(refund_status_code__isnull=False)
        ).only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'status', 'payment_mode', 'paid_amount',
            'payee_first_name', 'payee_mid_name', 'payee_lst_name',
            'refund_date', 'refunded_date', 'refund_track_id',
            'refund_message', 'refund_status_code',
            'refund_request_from', 'pg_name', 'bank_txn_id'
        )

        # Filter by merchant's client_code
        if hasattr(self.request.user, 'client_code'):
            queryset = queryset.filter(client_code=self.request.user.client_code)

        return queryset

    @CacheDecorator.cache_result(timeout=300, key_prefix='merchant_refund_history')  # 5 min cache
    def list(self, request, *args, **kwargs):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get base queryset
        queryset = self.get_queryset()

        # Apply comprehensive filters (merchant context already applied in get_queryset)
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # Refund-specific filters
        refund_status = request.query_params.get('refund_status')
        if refund_status:
            queryset = queryset.filter(refund_status_code=refund_status)

        refund_message = request.query_params.get('refund_message')
        if refund_message:
            queryset = queryset.filter(refund_message__icontains=refund_message)

        refund_status_code = request.query_params.get('refund_status_code')
        if refund_status_code:
            queryset = queryset.filter(refund_status_code=refund_status_code)

        refund_request_from = request.query_params.get('refund_request_from')
        if refund_request_from:
            queryset = queryset.filter(refund_request_from__icontains=refund_request_from)

        refund_reason = request.query_params.get('refund_reason')
        if refund_reason:
            # Filter by refund_message or refund_request_from as proxy for reason
            queryset = queryset.filter(
                Q(refund_message__icontains=refund_reason) |
                Q(refund_request_from__icontains=refund_reason)
            )

        refund_track_id = request.query_params.get('refund_track_id')
        if refund_track_id:
            queryset = queryset.filter(refund_track_id=refund_track_id)

        # Date filters
        refund_date = request.query_params.get('refund_date')
        if refund_date:
            # Single date filter
            queryset = queryset.filter(refund_date__date=refund_date)
        else:
            # Use refund_date for date range filters if specified
            use_refund_date = request.query_params.get('use_refund_date', 'false').lower() == 'true'
            if use_refund_date:
                date_filter = request.query_params.get('date_filter', 'custom')
                if date_filter != 'custom':
                    date_from, date_to = TransactionSearchFilter.get_date_range(date_filter)
                    if date_from and date_to:
                        queryset = queryset.filter(refund_date__range=[date_from, date_to])
                else:
                    date_from = request.query_params.get('date_from')
                    date_to = request.query_params.get('date_to')
                    if date_from:
                        queryset = queryset.filter(refund_date__gte=date_from)
                    if date_to:
                        queryset = queryset.filter(refund_date__lte=date_to)

        # Refunded amount filters - use paid_amount as proxy since refund_amount doesn't exist
        refunded_amount = request.query_params.get('refunded_amount')
        if refunded_amount:
            try:
                queryset = queryset.filter(paid_amount=float(refunded_amount))
            except (ValueError, TypeError):
                pass
        else:
            min_refund_amount = request.query_params.get('min_refund_amount')
            max_refund_amount = request.query_params.get('max_refund_amount')
            if min_refund_amount:
                try:
                    queryset = queryset.filter(paid_amount__gte=float(min_refund_amount))
                except (ValueError, TypeError):
                    pass
            if max_refund_amount:
                try:
                    queryset = queryset.filter(paid_amount__lte=float(max_refund_amount))
                except (ValueError, TypeError):
                    pass

        # Order by refund date
        queryset = queryset.order_by('-refund_date', '-trans_date')

        # Generate filter summary
        filter_summary = f"Merchant: {request.user.username}"
        filter_summary += TransactionSearchFilter.get_filter_summary(request.query_params)
        if refund_status:
            filter_summary += f" | Refund Status: {refund_status}"
        if refund_message:
            filter_summary += f" | Refund Message: {refund_message}"
        if refund_reason:
            filter_summary += f" | Refund Reason: {refund_reason}"
        if refund_track_id:
            filter_summary += f" | Track ID: {refund_track_id}"

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


class GetChargebackTxnHistoryView(generics.ListAPIView):
    """
    API endpoint: GetChargebackTxnHistory
    GET /api/v1/settlements/chargeback-history/
    Response time target: <158ms P95
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChargebackTransactionSerializer
    pagination_class = CustomPostPagination

    def get_queryset(self):
        # Get chargeback transactions with safe fields
        queryset = TransactionDetail.objects.filter(
            Q(charge_back_amount__gt=0) |
            Q(charge_back_status__isnull=False)
        ).only(
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'status', 'payment_mode', 'paid_amount',
            'payee_first_name', 'payee_mid_name', 'payee_lst_name',
            'charge_back_amount', 'charge_back_date',
            'charge_back_status', 'chargeback_request_from',
            'pg_name', 'bank_txn_id'
        )
        return queryset

    @CacheDecorator.cache_result(timeout=300, key_prefix='chargeback_history')  # 5 min cache
    def list(self, request, *args, **kwargs):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
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

        # Chargeback-specific filters
        chargeback_status = request.query_params.get('chargeback_status')
        if chargeback_status:
            queryset = queryset.filter(charge_back_status=chargeback_status)

        chargeback_reason = request.query_params.get('chargeback_reason')
        if chargeback_reason:
            # Use chargeback_request_from as proxy since charge_back_reason may not exist
            queryset = queryset.filter(chargeback_request_from__icontains=chargeback_reason)

        # Use chargeback_date for date filters if specified
        use_chargeback_date = request.query_params.get('use_chargeback_date', 'false').lower() == 'true'
        if use_chargeback_date:
            date_filter = request.query_params.get('date_filter', 'custom')
            if date_filter != 'custom':
                date_from, date_to = TransactionSearchFilter.get_date_range(date_filter)
                if date_from and date_to:
                    queryset = queryset.filter(charge_back_date__range=[date_from, date_to])
            else:
                date_from = request.query_params.get('date_from')
                date_to = request.query_params.get('date_to')
                if date_from:
                    queryset = queryset.filter(charge_back_date__gte=date_from)
                if date_to:
                    queryset = queryset.filter(charge_back_date__lte=date_to)

        # Chargeback amount filters
        min_chargeback_amount = request.query_params.get('min_chargeback_amount')
        max_chargeback_amount = request.query_params.get('max_chargeback_amount')
        if min_chargeback_amount:
            try:
                queryset = queryset.filter(charge_back_amount__gte=float(min_chargeback_amount))
            except (ValueError, TypeError):
                pass
        if max_chargeback_amount:
            try:
                queryset = queryset.filter(charge_back_amount__lte=float(max_chargeback_amount))
            except (ValueError, TypeError):
                pass

        # Order by chargeback date
        queryset = queryset.order_by('-charge_back_date', '-trans_date')

        # Generate filter summary
        filter_summary = TransactionSearchFilter.get_filter_summary(request.query_params)
        if chargeback_status:
            filter_summary += f" | Chargeback Status: {chargeback_status}"
        if chargeback_reason:
            filter_summary += f" | Chargeback Reason: {chargeback_reason}"

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


class ReconciliationView(views.APIView):
    """
    Three-way reconciliation endpoint
    POST /api/v1/settlements/reconciliation/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        # This would implement three-way reconciliation logic
        # Comparing bank statements, gateway data, and internal records
        return Response({
            'success': True,
            'message': 'Reconciliation initiated',
            'reconciliation_id': 'REC123456'
        }, status=status.HTTP_202_ACCEPTED)