"""
Celery tasks for maintaining aggregation tables
Runs periodically to pre-calculate statistics for fast queries
"""
from celery import shared_task
from django.db import transaction, connection
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)


@shared_task(name='update_daily_summaries')
def update_daily_transaction_summaries(date_str: str = None):
    """
    Update daily transaction summaries for a specific date
    If no date provided, updates yesterday's data

    This task should run daily at midnight to summarize previous day
    Can also be triggered on-demand for specific dates
    """
    from apps.transactions.models import TransactionDetail
    from apps.transactions.models_aggregations import DailyTransactionSummary

    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        # Default to yesterday
        target_date = (timezone.now() - timedelta(days=1)).date()

    logger.info(f"Updating daily summaries for {target_date}")

    start_time = timezone.now()

    # Get all transactions for the target date
    transactions = TransactionDetail.objects.filter(
        trans_date__date=target_date
    )

    # Group by client_code and calculate aggregations
    summary_data = transactions.values('client_code', 'client_name').annotate(
        total_count=Count('txn_id'),
        success_count=Count('txn_id', filter=Q(status='SUCCESS')),
        failed_count=Count('txn_id', filter=Q(status='FAILED')),
        pending_count=Count('txn_id', filter=Q(status='PENDING')),
        total_amount=Sum('paid_amount'),
        success_amount=Sum('paid_amount', filter=Q(status='SUCCESS')),
        failed_amount=Sum('paid_amount', filter=Q(status='FAILED')),
        settled_count=Count('txn_id', filter=Q(is_settled=True)),
        settled_amount=Sum('settlement_amount', filter=Q(is_settled=True)),
        unsettled_count=Count('txn_id', filter=Q(is_settled=False)),
        refund_count=Count('txn_id', filter=Q(refund_date__isnull=False)),
        refund_amount=Sum('paid_amount', filter=Q(refund_date__isnull=False)),
        chargeback_count=Count('txn_id', filter=Q(charge_back_date__isnull=False)),
        chargeback_amount=Sum('charge_back_amount', filter=Q(charge_back_date__isnull=False)),
    )

    # Bulk update or create summaries
    summaries_created = 0
    summaries_updated = 0

    for data in summary_data:
        client_code = data['client_code']
        if not client_code:
            continue

        # Calculate unsettled amount
        unsettled_amount = (data['success_amount'] or 0) - (data['settled_amount'] or 0)

        summary, created = DailyTransactionSummary.objects.update_or_create(
            date=target_date,
            client_code=client_code,
            defaults={
                'client_name': data['client_name'],
                'total_count': data['total_count'] or 0,
                'success_count': data['success_count'] or 0,
                'failed_count': data['failed_count'] or 0,
                'pending_count': data['pending_count'] or 0,
                'total_amount': data['total_amount'] or 0,
                'success_amount': data['success_amount'] or 0,
                'failed_amount': data['failed_amount'] or 0,
                'settled_count': data['settled_count'] or 0,
                'settled_amount': data['settled_amount'] or 0,
                'unsettled_count': data['unsettled_count'] or 0,
                'unsettled_amount': unsettled_amount,
                'refund_count': data['refund_count'] or 0,
                'refund_amount': data['refund_amount'] or 0,
                'chargeback_count': data['chargeback_count'] or 0,
                'chargeback_amount': data['chargeback_amount'] or 0,
            }
        )

        if created:
            summaries_created += 1
        else:
            summaries_updated += 1

    duration = (timezone.now() - start_time).total_seconds()

    logger.info(
        f"Daily summary update completed for {target_date} in {duration:.2f}s | "
        f"Created: {summaries_created}, Updated: {summaries_updated}"
    )

    return {
        'date': str(target_date),
        'created': summaries_created,
        'updated': summaries_updated,
        'duration_seconds': duration
    }


@shared_task(name='update_payment_mode_summaries')
def update_payment_mode_summaries(date_str: str = None):
    """
    Update payment mode wise summaries
    """
    from apps.transactions.models import TransactionDetail
    from apps.transactions.models_aggregations import PaymentModeSummary

    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = (timezone.now() - timedelta(days=1)).date()

    logger.info(f"Updating payment mode summaries for {target_date}")

    transactions = TransactionDetail.objects.filter(
        trans_date__date=target_date
    )

    # Group by client_code and payment_mode
    summary_data = transactions.values('client_code', 'payment_mode').annotate(
        total_count=Count('txn_id'),
        success_count=Count('txn_id', filter=Q(status='SUCCESS')),
        failed_count=Count('txn_id', filter=Q(status='FAILED')),
        total_amount=Sum('paid_amount'),
        success_amount=Sum('paid_amount', filter=Q(status='SUCCESS')),
        avg_amount=Avg('paid_amount'),
    )

    summaries_processed = 0

    for data in summary_data:
        if not data['client_code'] or not data['payment_mode']:
            continue

        PaymentModeSummary.objects.update_or_create(
            date=target_date,
            client_code=data['client_code'],
            payment_mode=data['payment_mode'],
            defaults={
                'total_count': data['total_count'] or 0,
                'success_count': data['success_count'] or 0,
                'failed_count': data['failed_count'] or 0,
                'total_amount': data['total_amount'] or 0,
                'success_amount': data['success_amount'] or 0,
                'avg_transaction_amount': data['avg_amount'] or 0,
            }
        )
        summaries_processed += 1

    logger.info(f"Payment mode summaries updated: {summaries_processed} records")
    return {'date': str(target_date), 'processed': summaries_processed}


@shared_task(name='update_hourly_stats')
def update_hourly_transaction_stats():
    """
    Update hourly statistics for the current hour
    Should run every hour
    """
    from apps.transactions.models import TransactionDetail
    from apps.transactions.models_aggregations import HourlyTransactionStats

    current_time = timezone.now()
    current_date = current_time.date()
    current_hour = current_time.hour

    logger.info(f"Updating hourly stats for {current_date} {current_hour}:00")

    # Get transactions for current hour
    hour_start = current_time.replace(minute=0, second=0, microsecond=0)
    hour_end = hour_start + timedelta(hours=1)

    transactions = TransactionDetail.objects.filter(
        trans_date__gte=hour_start,
        trans_date__lt=hour_end
    )

    # Overall stats (all merchants)
    overall_stats = transactions.aggregate(
        total_count=Count('txn_id'),
        success_count=Count('txn_id', filter=Q(status='SUCCESS')),
        failed_count=Count('txn_id', filter=Q(status='FAILED')),
        total_amount=Sum('paid_amount'),
        success_amount=Sum('paid_amount', filter=Q(status='SUCCESS')),
    )

    HourlyTransactionStats.objects.update_or_create(
        date=current_date,
        hour=current_hour,
        client_code=None,  # Overall stats
        defaults={
            'total_count': overall_stats['total_count'] or 0,
            'success_count': overall_stats['success_count'] or 0,
            'failed_count': overall_stats['failed_count'] or 0,
            'total_amount': overall_stats['total_amount'] or 0,
            'success_amount': overall_stats['success_amount'] or 0,
        }
    )

    # Per-merchant stats
    merchant_stats = transactions.values('client_code').annotate(
        total_count=Count('txn_id'),
        success_count=Count('txn_id', filter=Q(status='SUCCESS')),
        failed_count=Count('txn_id', filter=Q(status='FAILED')),
        total_amount=Sum('paid_amount'),
        success_amount=Sum('paid_amount', filter=Q(status='SUCCESS')),
    )

    for stats in merchant_stats:
        if not stats['client_code']:
            continue

        HourlyTransactionStats.objects.update_or_create(
            date=current_date,
            hour=current_hour,
            client_code=stats['client_code'],
            defaults={
                'total_count': stats['total_count'] or 0,
                'success_count': stats['success_count'] or 0,
                'failed_count': stats['failed_count'] or 0,
                'total_amount': stats['total_amount'] or 0,
                'success_amount': stats['success_amount'] or 0,
            }
        )

    logger.info(f"Hourly stats updated for {current_date} {current_hour}:00")
    return {'date': str(current_date), 'hour': current_hour}


@shared_task(name='update_monthly_stats')
def update_monthly_merchant_stats(year: int = None, month: int = None):
    """
    Update monthly statistics for merchants
    Should run at the end of each month
    """
    from apps.transactions.models import TransactionDetail
    from apps.transactions.models_aggregations import MerchantMonthlyStats

    if year is None or month is None:
        # Default to last month
        last_month = timezone.now().replace(day=1) - timedelta(days=1)
        year = last_month.year
        month = last_month.month

    logger.info(f"Updating monthly stats for {year}-{month:02d}")

    # Get date range for the month
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    transactions = TransactionDetail.objects.filter(
        trans_date__gte=month_start,
        trans_date__lt=month_end
    )

    # Group by merchant
    merchant_stats = transactions.values('client_code').annotate(
        total_count=Count('txn_id'),
        success_count=Count('txn_id', filter=Q(status='SUCCESS')),
        failed_count=Count('txn_id', filter=Q(status='FAILED')),
        total_amount=Sum('paid_amount'),
        success_amount=Sum('paid_amount', filter=Q(status='SUCCESS')),
        settled_amount=Sum('settlement_amount', filter=Q(is_settled=True)),
        avg_amount=Avg('paid_amount'),
        unique_customers=Count('payee_email', distinct=True),
    )

    stats_processed = 0

    for stats in merchant_stats:
        if not stats['client_code']:
            continue

        pending_settlement = (stats['success_amount'] or 0) - (stats['settled_amount'] or 0)

        MerchantMonthlyStats.objects.update_or_create(
            year=year,
            month=month,
            client_code=stats['client_code'],
            defaults={
                'total_count': stats['total_count'] or 0,
                'success_count': stats['success_count'] or 0,
                'failed_count': stats['failed_count'] or 0,
                'total_amount': stats['total_amount'] or 0,
                'success_amount': stats['success_amount'] or 0,
                'settled_amount': stats['settled_amount'] or 0,
                'pending_settlement': pending_settlement,
                'unique_customers': stats['unique_customers'] or 0,
                'average_transaction_value': stats['avg_amount'] or 0,
            }
        )
        stats_processed += 1

    logger.info(f"Monthly stats updated for {year}-{month:02d}: {stats_processed} merchants")
    return {'year': year, 'month': month, 'processed': stats_processed}


@shared_task(name='cleanup_old_cache')
def cleanup_expired_search_cache():
    """
    Clean up expired search cache entries
    Runs daily
    """
    from apps.transactions.models_aggregations import TransactionSearchCache

    expired_count = TransactionSearchCache.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()[0]

    logger.info(f"Cleaned up {expired_count} expired cache entries")
    return {'deleted': expired_count}


@shared_task(name='batch_update_all_summaries')
def batch_update_all_summaries(date_range_days: int = 30):
    """
    Batch update all summary tables for a date range
    Useful for initial setup or backfilling data

    Args:
        date_range_days: Number of days to process (default: 30)
    """
    logger.info(f"Starting batch update for last {date_range_days} days")

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=date_range_days)

    results = {
        'daily_summaries': 0,
        'payment_mode_summaries': 0,
        'errors': []
    }

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')

        try:
            # Update daily summaries
            result = update_daily_transaction_summaries(date_str)
            results['daily_summaries'] += result['created'] + result['updated']

            # Update payment mode summaries
            pm_result = update_payment_mode_summaries(date_str)
            results['payment_mode_summaries'] += pm_result['processed']

        except Exception as e:
            error_msg = f"Error processing {date_str}: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        current_date += timedelta(days=1)

    logger.info(f"Batch update completed: {results}")
    return results
