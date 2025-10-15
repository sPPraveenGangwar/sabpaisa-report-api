"""
Analytics views for business intelligence and reporting
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Avg, F, Value, CharField
from django.db.models.functions import TruncDate, TruncMonth, TruncHour, Concat
from django.utils import timezone
from datetime import datetime, timedelta
import json

from apps.core.permissions import IsAdmin, IsMerchant
from apps.core.cache import CacheDecorator
from apps.transactions.models import TransactionDetail, ClientDataTable
from apps.transactions.filters import TransactionSearchFilter


class MerchantAnalyticsView(views.APIView):
    """
    Comprehensive merchant analytics dashboard
    GET /api/v1/analytics/merchant-analytics/
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=1800)  # Cache for 30 minutes
    def get(self, request):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base queryset
        transactions = TransactionDetail.objects.all()

        # Apply comprehensive filters
        transactions = TransactionSearchFilter.apply_filters(
            transactions,
            request.query_params,
            request.user
        )

        # Determine the date range for analytics
        date_filter = request.query_params.get('date_filter', 'month')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # Set start_date and end_date based on filters
        if date_from and date_to:
            # Custom date range provided
            from datetime import datetime
            start_date = datetime.fromisoformat(date_from)
            end_date = datetime.fromisoformat(date_to)
            if not timezone.is_aware(start_date):
                start_date = timezone.make_aware(start_date)
            if not timezone.is_aware(end_date):
                end_date = timezone.make_aware(end_date)
        elif date_filter != 'custom':
            # Use predefined date filter
            start_date, end_date = TransactionSearchFilter.get_date_range(date_filter)
        else:
            # Default to last 30 days if no filter specified
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            transactions = transactions.filter(
                trans_date__gte=start_date,
                trans_date__lte=end_date
            )

        # Calculate days in period
        days = (end_date.date() - start_date.date()).days + 1 if hasattr(end_date, 'date') else 1

        # Calculate KPIs
        total_transactions = transactions.count()
        successful_transactions = transactions.filter(status='SUCCESS').count()
        failed_transactions = transactions.filter(status='FAILED').count()

        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0

        # Financial metrics
        total_volume = transactions.filter(status='SUCCESS').aggregate(
            Sum('paid_amount'))['paid_amount__sum'] or 0
        avg_transaction_value = transactions.filter(status='SUCCESS').aggregate(
            Avg('paid_amount'))['paid_amount__avg'] or 0

        # Settlement metrics
        settled_amount = transactions.filter(
            is_settled=True
        ).aggregate(Sum('settlement_amount'))['settlement_amount__sum'] or 0

        pending_settlement = transactions.filter(
            status='SUCCESS', is_settled=False
        ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0

        # Payment mode distribution
        payment_modes = transactions.filter(status='SUCCESS').values('payment_mode').annotate(
            count=Count('txn_id'),
            volume=Sum('paid_amount')
        ).order_by('-volume')[:5]

        # Daily trend
        daily_trend = transactions.values(
            date=TruncDate('trans_date')
        ).annotate(
            total=Count('txn_id'),
            successful=Count('txn_id', filter=Q(status='SUCCESS')),
            volume=Sum('paid_amount', filter=Q(status='SUCCESS'))
        ).order_by('date')

        # Hourly distribution - using Extract instead of TruncHour to avoid timezone issues
        from django.db.models import F
        from django.db.models.functions import Extract
        hourly_dist = transactions.filter(status='SUCCESS').annotate(
            hour=Extract('trans_date', 'hour')
        ).values('hour').annotate(
            count=Count('txn_id')
        ).order_by('hour')

        # Top customers
        top_customers = transactions.filter(status='SUCCESS').values(
            'payee_email'
        ).annotate(
            transaction_count=Count('txn_id'),
            total_amount=Sum('paid_amount')
        ).order_by('-total_amount')[:10]

        analytics_data = {
            'kpis': {
                'total_transactions': total_transactions,
                'successful_transactions': successful_transactions,
                'failed_transactions': failed_transactions,
                'success_rate': round(success_rate, 2),
                'total_volume': float(total_volume),
                'avg_transaction_value': float(avg_transaction_value),
                'settled_amount': float(settled_amount),
                'pending_settlement': float(pending_settlement)
            },
            'payment_mode_distribution': [
                {
                    'mode': pm['payment_mode'] or 'Unknown',
                    'count': pm['count'],
                    'volume': float(pm['volume'] or 0)
                } for pm in payment_modes
            ],
            'daily_trend': [
                {
                    'date': dt['date'].isoformat() if dt['date'] else None,
                    'total': dt['total'],
                    'successful': dt['successful'],
                    'volume': float(dt['volume'] or 0)
                } for dt in daily_trend
            ],
            'hourly_distribution': [
                {
                    'hour': hd['hour'] if hd['hour'] is not None else 0,
                    'count': hd['count']
                } for hd in hourly_dist
            ],
            'top_customers': [
                {
                    'email': tc['payee_email'],
                    'transaction_count': tc['transaction_count'],
                    'total_amount': float(tc['total_amount'] or 0)
                } for tc in top_customers if tc['payee_email']
            ],
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }

        return Response({
            'success': True,
            'data': analytics_data
        })


class PaymentModeAnalyticsView(views.APIView):
    """
    Payment mode specific analytics
    GET /api/v1/analytics/payment-mode-analytics/
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=900, key_prefix='payment_mode_analytics')  # 15 min cache
    def get(self, request):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base queryset with safe fields only
        queryset = TransactionDetail.objects.all().only(
            'txn_id', 'client_code', 'client_name', 'trans_date', 'trans_complete_date',
            'status', 'payment_mode', 'paid_amount', 'pg_name',
            'is_settled', 'settlement_amount'
        )

        # Apply comprehensive filters
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # If no payment mode specified, default to UPI
        payment_mode = request.query_params.get('payment_mode', 'UPI')
        if not request.query_params.get('payment_mode'):
            queryset = queryset.filter(payment_mode__icontains=payment_mode)

        # If no date filter specified, default to last 7 days
        if not request.query_params.get('date_filter') and not request.query_params.get('date_from'):
            end_date = timezone.now()
            start_date = end_date - timedelta(days=7)
            queryset = queryset.filter(
                trans_date__gte=start_date,
                trans_date__lte=end_date
            )

        # Calculate metrics
        total = queryset.count()
        successful = queryset.filter(status='SUCCESS').count()
        failed = queryset.filter(status='FAILED').count()

        volume = queryset.filter(status='SUCCESS').aggregate(
            Sum('paid_amount'))['paid_amount__sum'] or 0

        avg_amount = queryset.filter(status='SUCCESS').aggregate(
            Avg('paid_amount'))['paid_amount__avg'] or 0

        # Success rate by bank/gateway
        gateway_stats = queryset.values('pg_name').annotate(
            total=Count('txn_id'),
            successful=Count('txn_id', filter=Q(status='SUCCESS')),
            volume=Sum('paid_amount', filter=Q(status='SUCCESS'))
        ).order_by('-volume')

        # Trend analysis
        trend = queryset.values(
            date=TruncDate('trans_date')
        ).annotate(
            count=Count('txn_id'),
            success_count=Count('txn_id', filter=Q(status='SUCCESS')),
            volume=Sum('paid_amount', filter=Q(status='SUCCESS'))
        ).order_by('date')

        return Response({
            'success': True,
            'data': {
                'payment_mode': payment_mode,
                'metrics': {
                    'total_transactions': total,
                    'successful': successful,
                    'failed': failed,
                    'success_rate': round((successful/total*100) if total > 0 else 0, 2),
                    'total_volume': float(volume),
                    'avg_transaction': float(avg_amount)
                },
                'gateway_performance': [
                    {
                        'gateway': gs['pg_name'] or 'Unknown',
                        'total': gs['total'],
                        'successful': gs['successful'],
                        'success_rate': round((gs['successful']/gs['total']*100) if gs['total'] > 0 else 0, 2),
                        'volume': float(gs['volume'] or 0)
                    } for gs in gateway_stats
                ],
                'daily_trend': [
                    {
                        'date': t['date'].isoformat() if t['date'] else None,
                        'count': t['count'],
                        'successful': t['success_count'],
                        'volume': float(t['volume'] or 0)
                    } for t in trend
                ]
            }
        })


class SettlementAnalyticsView(views.APIView):
    """
    Settlement analytics and reconciliation metrics
    GET /api/v1/analytics/settlement-analytics/
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=900, key_prefix='settlement_analytics')  # 15 min cache
    def get(self, request):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base queryset - only successful transactions for settlement analytics
        # Use only() to select safe fields and avoid non-existent columns
        queryset = TransactionDetail.objects.filter(status='SUCCESS').only(
            'txn_id', 'client_code', 'client_name', 'trans_date', 'trans_complete_date',
            'status', 'payment_mode', 'paid_amount', 'is_settled', 'settlement_date',
            'settlement_amount', 'settlement_status', 'bank_txn_id', 'pg_name'
        )

        # Apply comprehensive filters
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # If no date filter specified, default to last 30 days
        if not request.query_params.get('date_filter') and not request.query_params.get('date_from'):
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            queryset = queryset.filter(
                trans_date__gte=start_date,
                trans_date__lte=end_date
            )

        # Settlement metrics
        total_success = queryset.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        total_settled = queryset.filter(is_settled=True).aggregate(
            Sum('settlement_amount'))['settlement_amount__sum'] or 0
        pending_settlement = queryset.filter(is_settled=False).aggregate(
            Sum('paid_amount'))['paid_amount__sum'] or 0

        # Settlement timeline
        settlement_timeline = queryset.filter(is_settled=True).values(
            date=TruncDate('settlement_date')
        ).annotate(
            count=Count('txn_id'),
            amount=Sum('settlement_amount')
        ).order_by('-date')[:30]

        # Settlement TAT (Turn Around Time)
        from django.db.models import ExpressionWrapper, DurationField
        tat_data = queryset.filter(
            is_settled=True,
            settlement_date__isnull=False
        ).annotate(
            tat=ExpressionWrapper(
                F('settlement_date') - F('trans_complete_date'),
                output_field=DurationField()
            )
        )

        # Calculate average TAT in hours
        avg_tat_seconds = 0
        tat_count = 0
        for txn in tat_data[:1000]:  # Sample for performance
            if txn.tat:
                avg_tat_seconds += txn.tat.total_seconds()
                tat_count += 1

        avg_tat_hours = (avg_tat_seconds / tat_count / 3600) if tat_count > 0 else 0

        # Bank-wise settlement (using pg_name as proxy for bank)
        bank_settlements = queryset.filter(is_settled=True).values('pg_name').annotate(
            count=Count('txn_id'),
            amount=Sum('settlement_amount')
        ).order_by('-amount')

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_transaction_amount': float(total_success),
                    'total_settled': float(total_settled),
                    'pending_settlement': float(pending_settlement),
                    'settlement_rate': round((total_settled/total_success*100) if total_success > 0 else 0, 2),
                    'avg_settlement_tat_hours': round(avg_tat_hours, 2)
                },
                'settlement_timeline': [
                    {
                        'date': st['date'].isoformat() if st['date'] else None,
                        'count': st['count'],
                        'amount': float(st['amount'] or 0)
                    } for st in settlement_timeline
                ],
                'bank_wise_settlement': [
                    {
                        'bank': bs['pg_name'] or 'Unknown',
                        'count': bs['count'],
                        'amount': float(bs['amount'] or 0)
                    } for bs in bank_settlements
                ]
            }
        })


class RefundChargebackAnalyticsView(views.APIView):
    """
    Refund and chargeback analytics
    GET /api/v1/analytics/refund-chargeback/
    """
    permission_classes = [IsAuthenticated]

    @CacheDecorator.cache_result(timeout=1800, key_prefix='refund_chargeback_analytics')  # 30 min cache
    def get(self, request):
        # Validate filters
        filter_errors = TransactionSearchFilter.validate_filters(request.query_params)
        if filter_errors:
            return Response({
                'success': False,
                'message': 'Invalid filter parameters',
                'errors': filter_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base queryset with safe fields only
        # Note: refund_amount, refunded_amount and is_charge_back don't exist in the model
        queryset = TransactionDetail.objects.all().only(
            'txn_id', 'client_code', 'client_name', 'trans_date', 'status',
            'payment_mode', 'paid_amount', 'refund_date', 'refunded_date',
            'charge_back_amount', 'charge_back_date', 'charge_back_status',
            'refund_message', 'refund_status_code', 'refund_request_from',
            'chargeback_request_from'
        )

        # Apply comprehensive filters
        queryset = TransactionSearchFilter.apply_filters(
            queryset,
            request.query_params,
            request.user
        )

        # If no date filter specified, default to last 30 days
        if not request.query_params.get('date_filter') and not request.query_params.get('date_from'):
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            queryset = queryset.filter(
                trans_date__gte=start_date,
                trans_date__lte=end_date
            )

        # Refund metrics (no refund_amount or refunded_amount fields exist)
        # Using refund_date and refund_status_code to identify refunds
        total_refunds = queryset.filter(
            Q(refund_date__isnull=False) | Q(refund_status_code__isnull=False)
        ).count()

        # Calculate refund amount using paid_amount as proxy
        refund_transactions = queryset.filter(
            Q(refund_date__isnull=False) | Q(refund_status_code__isnull=False)
        )
        refund_amount = refund_transactions.aggregate(
            total=Sum('paid_amount')  # Using paid_amount as proxy for refund amount
        )

        # Chargeback metrics (is_charge_back field doesn't exist)
        total_chargebacks = queryset.filter(
            Q(charge_back_amount__gt=0) | Q(charge_back_status__isnull=False)
        ).count()

        chargeback_amount = queryset.filter(
            Q(charge_back_amount__gt=0) | Q(charge_back_status__isnull=False)
        ).aggregate(Sum('charge_back_amount'))['charge_back_amount__sum'] or 0

        # Refund trend
        refund_trend = queryset.filter(
            Q(refund_date__isnull=False) | Q(refund_status_code__isnull=False)
        ).values(
            date=TruncDate('refund_date')
        ).annotate(
            count=Count('txn_id'),
            amount=Sum('paid_amount')  # Using paid_amount as proxy
        ).order_by('date')

        # Chargeback trend
        chargeback_trend = queryset.filter(
            Q(charge_back_amount__gt=0) | Q(charge_back_status__isnull=False)
        ).values(
            date=TruncDate('charge_back_date')
        ).annotate(
            count=Count('txn_id'),
            amount=Sum('charge_back_amount')
        ).order_by('date')

        # Refund reasons (using refund_message and refund_request_from as proxies)
        # Group by refund_message to get top reasons
        refund_reasons = queryset.filter(
            Q(refund_message__isnull=False) | Q(refund_request_from__isnull=False)
        ).values('refund_message').annotate(
            count=Count('txn_id')
        ).order_by('-count')[:10]

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_refunds': total_refunds,
                    'total_refund_amount': float(refund_amount['total'] or 0),
                    'refunded_amount': float(refund_amount['total'] or 0),  # Same as total since we don't have separate field
                    'total_chargebacks': total_chargebacks,
                    'total_chargeback_amount': float(chargeback_amount)
                },
                'refund_trend': [
                    {
                        'date': rt['date'].isoformat() if rt['date'] else None,
                        'count': rt['count'],
                        'amount': float(rt['amount'] or 0)
                    } for rt in refund_trend if rt['date']
                ],
                'chargeback_trend': [
                    {
                        'date': ct['date'].isoformat() if ct['date'] else None,
                        'count': ct['count'],
                        'amount': float(ct['amount'] or 0)
                    } for ct in chargeback_trend if ct['date']
                ],
                'top_refund_reasons': [
                    {
                        'reason': rr['refund_message'] or 'Not specified',
                        'count': rr['count']
                    } for rr in refund_reasons if rr['refund_message']
                ]
            }
        })


class ComparativeAnalyticsView(views.APIView):
    """
    Comparative analytics between periods or merchants
    GET /api/v1/analytics/comparative/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @CacheDecorator.cache_result(timeout=1800, key_prefix='comparative_analytics')  # 30 min cache
    def get(self, request):
        comparison_type = request.query_params.get('type', 'period')  # period or merchant

        if comparison_type == 'period':
            return self.compare_periods(request)
        else:
            return self.compare_merchants(request)

    def compare_periods(self, request):
        # Current period
        try:
            current_days = int(request.query_params.get('current_days', 30))
        except (ValueError, TypeError):
            current_days = 30  # Default to 30 days
        current_end = timezone.now()
        current_start = current_end - timedelta(days=current_days)

        # Previous period
        previous_end = current_start
        previous_start = previous_end - timedelta(days=current_days)

        # Get metrics for both periods
        def get_period_metrics(start_date, end_date):
            queryset = TransactionDetail.objects.filter(
                trans_date__gte=start_date,
                trans_date__lte=end_date
            ).only(
                'txn_id', 'trans_date', 'status', 'paid_amount'
            )

            total = queryset.count()
            successful = queryset.filter(status='SUCCESS').count()
            volume = queryset.filter(status='SUCCESS').aggregate(
                Sum('paid_amount'))['paid_amount__sum'] or 0

            return {
                'total_transactions': total,
                'successful_transactions': successful,
                'success_rate': round((successful/total*100) if total > 0 else 0, 2),
                'total_volume': float(volume)
            }

        current_metrics = get_period_metrics(current_start, current_end)
        previous_metrics = get_period_metrics(previous_start, previous_end)

        # Calculate changes
        changes = {}
        for key in current_metrics:
            if isinstance(current_metrics[key], (int, float)):
                prev_val = previous_metrics[key]
                curr_val = current_metrics[key]
                if prev_val > 0:
                    change_pct = ((curr_val - prev_val) / prev_val) * 100
                    changes[f'{key}_change'] = round(change_pct, 2)
                else:
                    changes[f'{key}_change'] = 100 if curr_val > 0 else 0

        return Response({
            'success': True,
            'data': {
                'current_period': {
                    'start': current_start.isoformat(),
                    'end': current_end.isoformat(),
                    'metrics': current_metrics
                },
                'previous_period': {
                    'start': previous_start.isoformat(),
                    'end': previous_end.isoformat(),
                    'metrics': previous_metrics
                },
                'changes': changes
            }
        })

    def compare_merchants(self, request):
        merchant_codes = request.query_params.get('merchant_codes', '').split(',')
        if len(merchant_codes) < 2:
            return Response({
                'success': False,
                'message': 'Please provide at least 2 merchant codes separated by comma'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            days = int(request.query_params.get('days', 30))
        except (ValueError, TypeError):
            days = 30  # Default to 30 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        merchant_data = []
        for code in merchant_codes[:5]:  # Limit to 5 merchants
            queryset = TransactionDetail.objects.filter(
                client_code=code.strip(),
                trans_date__gte=start_date,
                trans_date__lte=end_date
            ).only(
                'txn_id', 'client_code', 'trans_date', 'status', 'paid_amount'
            )

            total = queryset.count()
            successful = queryset.filter(status='SUCCESS').count()
            volume = queryset.filter(status='SUCCESS').aggregate(
                Sum('paid_amount'))['paid_amount__sum'] or 0

            merchant_data.append({
                'merchant_code': code.strip(),
                'total_transactions': total,
                'successful_transactions': successful,
                'success_rate': round((successful/total*100) if total > 0 else 0, 2),
                'total_volume': float(volume),
                'avg_transaction': float(volume/successful) if successful > 0 else 0
            })

        # Sort by volume
        merchant_data.sort(key=lambda x: x['total_volume'], reverse=True)

        return Response({
            'success': True,
            'data': {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'merchants': merchant_data
            }
        })


class ExecutiveDashboardView(views.APIView):
    """
    Executive dashboard with high-level KPIs
    GET /api/v1/analytics/executive-dashboard/
    Query params: date_filter (optional) - today|week|month|year
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        import logging
        from django.core.cache import cache
        from django.db import connection
        logger = logging.getLogger(__name__)

        # Ensure database connection is alive
        try:
            connection.ensure_connection()
        except Exception as e:
            logger.warning(f"Reconnecting to database: {e}")
            connection.close()
            connection.connect()

        # Get date filter from request (today, week, month, year)
        # DEFAULT: 'today' - load today's data by default on first page load
        date_filter = request.query_params.get('date_filter', 'today')

        # Calculate local timezone date for cache key
        import pytz
        local_tz = pytz.timezone('Asia/Kolkata')
        local_now = timezone.now().astimezone(local_tz)
        local_date = local_now.date()

        # PERFORMANCE: Cache dashboard data for 5 minutes
        cache_key = f'executive_dashboard_{date_filter}_{local_date}'
        cached_response = cache.get(cache_key)

        if cached_response:
            logger.info(f"Cache HIT for {cache_key} - Returning cached data")
            return Response(cached_response)

        logger.info(f"Cache MISS for {cache_key} - Calculating fresh data")

        # Calculate date range based on filter
        # Convert to local timezone (Asia/Kolkata) to match database
        from datetime import datetime

        now_local = local_now  # Already calculated above

        # Get start and end of day in local timezone
        today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end_local = now_local.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Pre-calculate month and year start for later use
        month_start = today_start_local.replace(day=1)
        year_start = today_start_local.replace(month=1, day=1)

        if date_filter == 'today':
            range_start = today_start_local
            range_end = today_end_local
        elif date_filter == 'week':
            # Last 7 days from today (not start of week)
            range_start = today_start_local - timedelta(days=6)  # 6 days ago + today = 7 days
            range_end = today_end_local
        elif date_filter == 'year':
            # Start of year in local timezone
            range_start = today_start_local.replace(month=1, day=1)
            range_end = today_end_local
        else:  # month (default)
            # Start of month in local timezone
            range_start = today_start_local.replace(day=1)
            range_end = today_end_local

        # Debug logging
        logger.debug("="*80)
        logger.debug(f"EXECUTIVE DASHBOARD DEBUG - Date Filter: {date_filter}")
        logger.debug(f"Range Start: {range_start}")
        logger.debug(f"Range End: {range_end}")

        # Count total transactions in DB
        total_in_db = TransactionDetail.objects.count()
        logger.debug(f"Total transactions in database: {total_in_db}")

        # Optimized: Use only required fields to reduce query size
        base_fields = ['txn_id', 'trans_date', 'status', 'paid_amount', 'client_code', 'client_name', 'payment_mode']

        # Get base queryset for selected range
        base_queryset = TransactionDetail.objects.filter(
            trans_date__gte=range_start,
            trans_date__lte=range_end
        )

        # Get total count
        total_records = base_queryset.count()
        logger.debug(f"Total transactions in range: {total_records}")

        logger.debug("=" * 80)

        # Early return if no data - skip expensive calculations
        if total_records == 0:
            logger.warning("WARNING: No transactions found in selected date range!")
            logger.info("TIP: Try using 'month' or 'year' filter to see historical data")
            logger.debug("="*80)

            # Return empty response immediately
            empty_response = {
                'success': True,
                'total_records': 0,
                'message': 'No transactions found in selected date range. Try a different time filter.',
                'data': {
                    'date_filter': date_filter,
                    'selected_range': {
                        'start_date': range_start.date().isoformat(),
                        'end_date': range_end.date().isoformat(),
                        'transactions': 0,
                        'volume': 0.0,
                        'success_rate': 0.0
                    },
                    'today': {'date': today_start_local.date().isoformat(), 'transactions': 0, 'volume': 0.0, 'success_rate': 0.0},
                    'month_to_date': {'start_date': month_start.date().isoformat(), 'end_date': today_end_local.date().isoformat(), 'transactions': 0, 'volume': 0.0, 'success_rate': 0.0},
                    'year_to_date': {'start_date': year_start.date().isoformat(), 'end_date': today_end_local.date().isoformat(), 'transactions': 0, 'volume': 0.0, 'success_rate': 0.0},
                    'merchants': {'total': 0, 'active': 0, 'activation_rate': 0.0},
                    'top_merchants': [],
                    'payment_mode_performance': [],
                    'daily_trend': [],
                    'recent_transactions': []
                }
            }

            # Don't cache empty results
            return Response(empty_response)

        # Data found - proceed with calculations
        logger.info(f"Found {total_records:,} transactions in date range")
        logger.debug("="*80)

        # ============================================================================
        # OPTIMIZED: Use raw SQL for faster aggregation on large datasets
        # ============================================================================

        try:
            import time
            from django.db import connection

            # Ensure connection is alive and reconnect if needed
            try:
                connection.ensure_connection()
                if connection.connection:
                    connection.connection.ping()
            except Exception:
                # Force reconnect if ping fails
                connection.close()
                connection.connect()

            with connection.cursor() as cursor:
                # Single optimized query to get all range stats
                sql_query = """
                    SELECT
                        COUNT(*) as total_transactions,
                        COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as success_transactions,
                        COALESCE(SUM(CASE WHEN status = 'SUCCESS' THEN paid_amount END), 0) as total_volume
                    FROM transaction_detail
                    WHERE trans_date >= %s AND trans_date <= %s
                """
                logger.debug(f"EXECUTING SQL QUERY (selected_range)")
                logger.debug(f"Query: {sql_query.strip()}")
                logger.debug(f"Params: range_start={range_start}, range_end={range_end}")
                logger.debug(f"Estimated records in range: checking...")

                start_time = time.time()
                cursor.execute(sql_query, [range_start, range_end])
                row = cursor.fetchone()
                elapsed = (time.time() - start_time) * 1000
                logger.debug(f"Query execution time: {elapsed:.2f}ms")
                logger.debug(f"Records found: {row[0] or 0}")

                range_stats = {
                    'total_transactions': row[0] or 0,
                    'success_transactions': row[1] or 0,
                    'total_volume': float(row[2] or 0)
                }
        except Exception as e:
            logger.error(f"Raw SQL failed: {str(e)[:200]}")
            logger.info("Falling back to ORM...")
            range_stats = base_queryset.aggregate(
                total_transactions=Count('txn_id'),
                success_transactions=Count('txn_id', filter=Q(status='SUCCESS')),
                total_volume=Sum('paid_amount', filter=Q(status='SUCCESS'))
            )
            range_stats = {
                'total_transactions': range_stats['total_transactions'] or 0,
                'success_transactions': range_stats['success_transactions'] or 0,
                'total_volume': float(range_stats['total_volume'] or 0)
            }

        range_metrics = {
            'transactions': range_stats['total_transactions'] or 0,
            'volume': float(range_stats['total_volume'] or 0),
            'success_rate': round(
                (range_stats['success_transactions'] / range_stats['total_transactions'] * 100)
                if range_stats['total_transactions'] > 0 else 0,
                2
            )
        }

        logger.debug(f"Selected range ALL records - Transactions: {range_metrics['transactions']}, Volume: {range_metrics['volume']}")
        logger.debug(f"Query uses fast aggregates (COUNT, SUM) - no individual record fetching")

        # ============================================================================
        # OPTIMIZATION: ONLY calculate the selected filter - no additional queries!
        # User selects 'today' → Only today's data calculated
        # User selects 'week' → Only week's data calculated
        # User selects 'month' → Only month's data calculated
        # User selects 'year' → Only year's data calculated
        # ============================================================================
        logger.info(f"Only calculated '{date_filter}' data - skipping all other time periods!")

        # ============================================================================
        # DETAIL QUERIES: Active merchants, top merchants, payment performance, etc.
        # ============================================================================

        # Reconnect database to ensure fresh connection
        logger.debug("Ensuring fresh database connection...")
        try:
            from django.db import connection
            connection.close()
            connection.connect()
            logger.debug("Database reconnected successfully")
        except Exception as e:
            logger.warning(f"Reconnection warning: {e}")

        # Active merchants - based on selected date range (today/week/month/year)
        try:
            import time
            from django.db import connection

            logger.debug(f"Fetching active merchants count (for {date_filter} range)...")
            start_time = time.time()

            # Use raw SQL for faster DISTINCT count
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(DISTINCT client_code)
                    FROM transaction_detail
                    WHERE trans_date >= %s AND trans_date <= %s
                """, [range_start, range_end])
                active_merchants = cursor.fetchone()[0] or 0

            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Active merchants in {date_filter}: {active_merchants} ({elapsed:.2f}ms)")
        except Exception as e:
            logger.error(f"Active merchants query failed: {e}")
            active_merchants = 0

        # Total merchants - cached count
        try:
            logger.debug("Fetching total merchants count...")
            start_time = time.time()

            total_merchants = ClientDataTable.objects.filter(active=True).count()

            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Total merchants: {total_merchants} ({elapsed:.2f}ms)")
        except Exception as e:
            logger.error(f"Total merchants query failed: {e}")
            total_merchants = 0

        # ============================================================================
        # OPTIMIZED DETAIL QUERIES: Use base_queryset (all records) but limit results
        # These use aggregates + LIMIT, so they're fast even on large datasets
        # ============================================================================

        # Top performing merchants from ALL records (limited to top 10)
        try:
            import time
            logger.debug("Fetching top merchants...")
            start_time = time.time()

            # Use raw SQL with optimized index hint for maximum performance
            # idx_status_date_client_amount is faster because status='SUCCESS' filter comes first
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        client_code,
                        client_name,
                        SUM(paid_amount) as volume,
                        COUNT(*) as count
                    FROM transaction_detail USE INDEX (idx_status_date_client_amount)
                    WHERE status = 'SUCCESS'
                        AND trans_date >= %s AND trans_date <= %s
                    GROUP BY client_code, client_name
                    ORDER BY volume DESC
                    LIMIT 10
                """, [range_start, range_end])

                top_merchants = [
                    {
                        'client_code': row[0],
                        'client_name': row[1],
                        'volume': float(row[2]) if row[2] else 0,
                        'count': row[3]
                    }
                    for row in cursor.fetchall()
                ]

            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Top merchants fetched: {len(top_merchants)} ({elapsed:.2f}ms)")
        except Exception as e:
            logger.error(f"Top merchants query failed: {e}")
            top_merchants = []

        # Payment mode performance from ALL records (limited to top 10 modes)
        try:
            import time
            logger.debug("Fetching payment performance...")
            start_time = time.time()

            # Use raw SQL with index hint for optimal performance
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        payment_mode,
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                        (SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
                    FROM transaction_detail USE INDEX (idx_trans_date_payment_status)
                    WHERE trans_date >= %s AND trans_date <= %s
                    GROUP BY payment_mode
                    ORDER BY total DESC
                    LIMIT 10
                """, [range_start, range_end])

                payment_performance = [
                    {
                        'payment_mode': row[0],
                        'total': row[1],
                        'successful': row[2],
                        'success_rate': float(row[3]) if row[3] else 0
                    }
                    for row in cursor.fetchall()
                ]

            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Payment performance fetched: {len(payment_performance)} modes ({elapsed:.2f}ms)")
        except Exception as e:
            logger.error(f"Payment performance query failed: {e}")
            payment_performance = []

        # Daily trend from ALL records (grouped by date - typically 1-365 rows)
        try:
            import time

            logger.debug("Fetching daily trend data...")
            start_time = time.time()

            # Use raw SQL with index hint for optimal performance
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        DATE(trans_date) as date_only,
                        COUNT(*) as transactions,
                        SUM(CASE WHEN status = 'SUCCESS' THEN paid_amount ELSE 0 END) as volume
                    FROM transaction_detail USE INDEX (idx_date_status_amount)
                    WHERE trans_date >= %s AND trans_date <= %s
                    GROUP BY DATE(trans_date)
                    ORDER BY date_only
                """, [range_start, range_end])

                daily_trend = [
                    {
                        'date': row[0],
                        'transactions': row[1],
                        'volume': float(row[2]) if row[2] else 0
                    }
                    for row in cursor.fetchall()
                ]

            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Daily trend fetched: {len(daily_trend)} data points ({elapsed:.2f}ms)")
            if daily_trend:
                for dt in daily_trend[:3]:  # Show first 3 entries
                    logger.debug(f"Date: {dt['date']}, Transactions: {dt['transactions']}, Volume: {dt['volume']}")
        except Exception as e:
            logger.error(f"Daily trend query failed: {e}")
            daily_trend = []

        # Recent transactions (latest 20 from all records, not paginated)
        try:
            import time
            logger.debug("Fetching recent transactions...")
            start_time = time.time()

            recent_txns = base_queryset.order_by('-trans_date')[:20].only(
                'txn_id', 'client_txn_id', 'paid_amount', 'status', 'payment_mode',
                'trans_date', 'client_name', 'client_code'
            ).values(
                'txn_id', 'client_txn_id', 'paid_amount', 'status', 'payment_mode',
                'trans_date', 'client_name', 'client_code'
            )

            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Recent transactions fetched: {len(list(recent_txns))} ({elapsed:.2f}ms)")
        except Exception as e:
            logger.error(f"Recent transactions query failed: {e}")
            recent_txns = []

        logger.info("All detail queries complete")

        # Build response data
        response_data = {
            'success': True,
            'total_records': total_records,
            'data': {
                'date_filter': date_filter,
                'selected_range': {
                    'start_date': range_start.date().isoformat(),
                    'end_date': range_end.date().isoformat(),
                    'transactions': range_metrics['transactions'],  # ONLY selected filter calculated
                    'volume': float(range_metrics['volume']),
                    'success_rate': range_metrics['success_rate']
                },
                # Removed: today, month_to_date, year_to_date
                # Now ONLY selected_range is calculated based on date_filter parameter
                'merchants': {
                    'total': total_merchants,
                    'active': active_merchants,
                    'activation_rate': round((active_merchants/total_merchants*100) if total_merchants > 0 else 0, 2)
                },
                'top_merchants': [
                    {
                        'code': tm['client_code'],
                        'name': tm['client_name'],
                        'volume': float(tm['volume']),
                        'transactions': tm['count']
                    } for tm in top_merchants
                ],
                'payment_mode_performance': [
                    {
                        'mode': pp['payment_mode'] or 'Unknown',
                        'total': pp['total'],
                        'successful': pp['successful'],
                        'success_rate': round(float(pp['success_rate']), 2)
                    } for pp in payment_performance if pp['payment_mode']
                ],
                'daily_trend': [
                    {
                        'date': dt['date'].strftime('%Y-%m-%d') if dt['date'] else None,
                        'transactions': dt['transactions'],
                        'volume': float(dt['volume'] or 0)
                    } for dt in daily_trend if dt['date']
                ],
                'recent_transactions': [
                    {
                        'id': txn['txn_id'] or txn.get('client_txn_id', 'N/A'),
                        'merchant': txn.get('client_name') or txn.get('client_code', 'Unknown'),
                        'amount': float(txn['paid_amount'] or 0),
                        'status': txn['status'],
                        'mode': txn['payment_mode'] or 'Unknown',
                        'date': txn['trans_date'].isoformat() if txn.get('trans_date') else None
                    } for txn in recent_txns
                ]
            }
        }

        # PERFORMANCE: Cache the response for 5 minutes (300 seconds)
        cache.set(cache_key, response_data, timeout=300)
        logger.info(f"Cached response for {cache_key} (5 min TTL)")

        return Response(response_data)

    def _calculate_success_rate(self, queryset):
        total = queryset.count()
        successful = queryset.filter(status='SUCCESS').count()
        return round((successful/total*100) if total > 0 else 0, 2)