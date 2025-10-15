"""
Advanced filters for transaction search
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

# Configure logger
logger = logging.getLogger('apps.transactions')
performance_logger = logging.getLogger('performance')


class TransactionSearchFilter:
    """
    Comprehensive transaction search filter handling all business cases
    """

    @staticmethod
    def get_date_range(date_filter):
        """
        Convert date filter string to date range

        Options:
        - today: Today's transactions
        - 3days: Last 3 days
        - week: Last 7 days
        - month: Current month
        - year: Current year
        - custom: Use date_from and date_to
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if date_filter == 'today':
            return today_start, today_end

        elif date_filter == '3days':
            start_date = today_start - timedelta(days=2)  # 2 days ago + today = 3 days
            return start_date, today_end

        elif date_filter == 'week':
            start_date = today_start - timedelta(days=6)  # 6 days ago + today = 7 days
            return start_date, today_end

        elif date_filter == 'month':
            # First day of current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return start_date, today_end

        elif date_filter == 'year':
            # First day of current year
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return start_date, today_end

        return None, None

    @staticmethod
    def apply_filters(queryset, request_data, user):
        """
        Apply all search filters based on the cases

        Cases:
        1. Admin can search merchant-wise or all merchants
        2. Date range filter (today/3days/week/month/year/custom)
        3. Payment mode filter (UPI/Intent/NB/CC/DC)
        4. Status filter (SUCCESS/FAILED/PENDING/ABORTED)
        5. Amount range filter (min_amount, max_amount)
        6. Search by txn_id or client_txn_id
        """
        logger.debug(f"Starting filter application for user: {getattr(user, 'username', 'Unknown')}")
        initial_count = queryset.count()
        filter_summary = []

        # CASE 1: Merchant filter (Admin can see all or specific merchant)
        if user.role == 'ADMIN':
            # Admin can filter by specific merchant or see all
            merchant_code = request_data.get('merchant_code') or request_data.get('client_code')
            if merchant_code and merchant_code != 'ALL':
                queryset = queryset.filter(client_code=merchant_code)
                filter_summary.append(f"Merchant: {merchant_code}")
                logger.debug(f"Applied merchant filter: {merchant_code}")
        else:
            # Non-admin users can only see their own merchant data
            if hasattr(user, 'client_code') and user.client_code:
                queryset = queryset.filter(client_code=user.client_code)
                logger.debug(f"Applied user merchant filter: {user.client_code}")

        # CASE 2: Date range filter
        # If date_from/date_to not provided, default to current date
        date_from = request_data.get('date_from')
        date_to = request_data.get('date_to')

        # Get today's date range for defaults
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Apply date_from filter (default to today if not provided)
        if date_from:
            if isinstance(date_from, str):
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                date_from = timezone.make_aware(date_from.replace(hour=0, minute=0, second=0))
            queryset = queryset.filter(trans_date__gte=date_from)
            filter_summary.append(f"From: {request_data.get('date_from')}")
            logger.debug(f"Applied date_from filter: {date_from}")
        else:
            # Default to today's start
            queryset = queryset.filter(trans_date__gte=today_start)
            filter_summary.append(f"From: {now.strftime('%Y-%m-%d')} (today)")
            logger.debug(f"Applied default date_from: {today_start}")

        # Apply date_to filter (default to today if not provided)
        if date_to:
            if isinstance(date_to, str):
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                date_to = timezone.make_aware(date_to.replace(hour=23, minute=59, second=59))
            queryset = queryset.filter(trans_date__lte=date_to)
            filter_summary.append(f"To: {request_data.get('date_to')}")
            logger.debug(f"Applied date_to filter: {date_to}")
        else:
            # Default to today's end
            queryset = queryset.filter(trans_date__lte=today_end)
            filter_summary.append(f"To: {now.strftime('%Y-%m-%d')} (today)")
            logger.debug(f"Applied default date_to: {today_end}")

        # CASE 3: Payment mode filter
        payment_mode = request_data.get('payment_mode')
        if payment_mode and payment_mode != 'ALL':
            # Handle multiple payment modes if comma-separated
            if ',' in payment_mode:
                payment_modes = [mode.strip() for mode in payment_mode.split(',')]
                # Use case-insensitive matching with Q objects
                q_filters = Q()
                for mode in payment_modes:
                    q_filters |= Q(payment_mode__iexact=mode)
                queryset = queryset.filter(q_filters)
                filter_summary.append(f"Payment modes: {payment_mode}")
                logger.debug(f"Applied payment mode filter: {payment_modes}")
            else:
                # Map common abbreviations to actual DB values
                payment_mode_mapping = {
                    'UPI': 'UPI',
                    'CC': 'Credit Card',
                    'DC': 'Debit Card',
                    'NB': 'Net Banking',
                    'WALLET': 'WALLET',
                    'INTENT': 'UPI INTENT',
                    'CASH': 'CASH',
                    'NEFT': 'NEFT',
                    'RUPAY': 'Rupay Card',
                    'RUPAYCREDIT': 'RuPayCreditCard',
                    'BHIM_UPI_QR': 'BHIM UPI QR',
                    'BHIM': 'BHIM UPI QR'
                }
                # Try to map first, otherwise use the value as-is
                mapped_mode = payment_mode_mapping.get(payment_mode.upper(), payment_mode)
                # Use case-insensitive exact match to handle any case variations
                queryset = queryset.filter(payment_mode__iexact=mapped_mode)
                filter_summary.append(f"Payment mode: {payment_mode}")
                logger.debug(f"Applied payment mode filter: {mapped_mode} (case-insensitive)")

        # CASE 4: Status filter
        status = request_data.get('status')
        if status and status != 'ALL':
            # Handle multiple statuses if comma-separated
            if ',' in status:
                statuses = [s.strip().upper() for s in status.split(',')]
                queryset = queryset.filter(status__in=statuses)
            else:
                queryset = queryset.filter(status=status.upper())

        # CASE 5: Amount range filter
        min_amount = request_data.get('min_amount')
        max_amount = request_data.get('max_amount')

        if min_amount:
            try:
                min_amount = float(min_amount)
                queryset = queryset.filter(paid_amount__gte=min_amount)
            except (ValueError, TypeError):
                pass

        if max_amount:
            try:
                max_amount = float(max_amount)
                queryset = queryset.filter(paid_amount__lte=max_amount)
            except (ValueError, TypeError):
                pass

        # CASE 6: Search by transaction ID
        txn_id = request_data.get('txn_id')
        client_txn_id = request_data.get('client_txn_id')

        if txn_id:
            queryset = queryset.filter(txn_id=txn_id)
        elif client_txn_id:
            queryset = queryset.filter(client_txn_id=client_txn_id)

        # Additional: General search field (searches multiple fields)
        search_query = request_data.get('search') or request_data.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(txn_id__icontains=search_query) |
                Q(client_txn_id__icontains=search_query) |
                Q(payee_email__icontains=search_query) |
                Q(payee_mob__icontains=search_query) |
                Q(bank_txn_id__icontains=search_query)
            )

        # Sorting
        order_by = request_data.get('order_by', '-trans_date')
        if order_by:
            # Validate the field exists to prevent SQL injection
            valid_fields = [
                'trans_date', '-trans_date',
                'paid_amount', '-paid_amount',
                'status', '-status',
                'client_code', '-client_code'
            ]
            if order_by in valid_fields:
                queryset = queryset.order_by(order_by)
                logger.debug(f"Applied sorting: {order_by}")
            else:
                queryset = queryset.order_by('-trans_date')
                logger.debug("Applied default sorting: -trans_date")

        # Log filter performance
        final_count = queryset.count()
        logger.info(f"Filter applied | Initial: {initial_count} | Final: {final_count} | Filters: {' | '.join(filter_summary) if filter_summary else 'None'}")
        performance_logger.info(f"Filter performance | User: {getattr(user, 'username', 'Unknown')} | Reduction: {initial_count - final_count} records")

        return queryset

    @staticmethod
    def get_filter_summary(request_data):
        """
        Generate a human-readable summary of applied filters
        """
        from django.utils import timezone

        summary = []

        # Date filter - always show date range
        date_from = request_data.get('date_from')
        date_to = request_data.get('date_to')

        if date_from and date_to:
            if date_from == date_to:
                summary.append(f"Date: {date_from}")
            else:
                summary.append(f"From {date_from} to {date_to}")
        elif date_from:
            summary.append(f"From {date_from}")
        elif date_to:
            summary.append(f"Until {date_to}")
        else:
            # Default: today's date
            today = timezone.now().strftime('%Y-%m-%d')
            summary.append(f"Date: {today} (Today)")

        # Merchant filter
        merchant_code = request_data.get('merchant_code') or request_data.get('client_code')
        if merchant_code and merchant_code != 'ALL':
            summary.append(f"Merchant: {merchant_code}")

        # Payment mode
        payment_mode = request_data.get('payment_mode')
        if payment_mode and payment_mode != 'ALL':
            summary.append(f"Payment mode: {payment_mode}")

        # Status
        status = request_data.get('status')
        if status and status != 'ALL':
            summary.append(f"Status: {status}")

        # Amount range
        min_amount = request_data.get('min_amount')
        max_amount = request_data.get('max_amount')
        if min_amount and max_amount:
            summary.append(f"Amount: ₹{min_amount} - ₹{max_amount}")
        elif min_amount:
            summary.append(f"Amount: ≥ ₹{min_amount}")
        elif max_amount:
            summary.append(f"Amount: ≤ ₹{max_amount}")

        # Transaction ID
        if request_data.get('txn_id'):
            summary.append(f"Transaction ID: {request_data.get('txn_id')}")
        elif request_data.get('client_txn_id'):
            summary.append(f"Client Transaction ID: {request_data.get('client_txn_id')}")

        return " | ".join(summary) if summary else "All transactions"

    @staticmethod
    def validate_filters(request_data):
        """
        Validate filter parameters
        """
        logger.debug(f"Validating filters: {dict(request_data)}")
        errors = {}

        # Validate date format
        date_from = request_data.get('date_from')
        date_to = request_data.get('date_to')

        if date_from:
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                errors['date_from'] = "Invalid date format. Use YYYY-MM-DD"

        if date_to:
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                errors['date_to'] = "Invalid date format. Use YYYY-MM-DD"

        # Validate date range logic
        if date_from and date_to and not errors:
            if date_from > date_to:
                errors['date_range'] = "From date cannot be after To date"

        # Validate amount range
        min_amount = request_data.get('min_amount')
        max_amount = request_data.get('max_amount')

        if min_amount:
            try:
                float(min_amount)
            except (ValueError, TypeError):
                errors['min_amount'] = "Invalid minimum amount"

        if max_amount:
            try:
                float(max_amount)
            except (ValueError, TypeError):
                errors['max_amount'] = "Invalid maximum amount"

        if min_amount and max_amount and not errors.get('min_amount') and not errors.get('max_amount'):
            if float(min_amount) > float(max_amount):
                errors['amount_range'] = "Minimum amount cannot be greater than maximum amount"

        # Validate status values
        status = request_data.get('status')
        if status and status != 'ALL':
            valid_statuses = ['SUCCESS', 'FAILED', 'PENDING', 'ABORTED']
            if ',' in status:
                statuses = [s.strip().upper() for s in status.split(',')]
                invalid = [s for s in statuses if s not in valid_statuses]
                if invalid:
                    errors['status'] = f"Invalid status values: {', '.join(invalid)}"
            elif status.upper() not in valid_statuses:
                errors['status'] = f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

        # Validate payment mode
        payment_mode = request_data.get('payment_mode')
        if payment_mode and payment_mode != 'ALL':
            # Include actual DB values and abbreviations
            valid_modes = [
                # Actual DB values
                'BHIM UPI QR', 'CASH', 'CREDIT CARD', 'DEBIT CARD', 'NEFT',
                'NET BANKING', 'RUPAY CARD', 'RUPAYCREDITCARD', 'UPI',
                'UPI INTENT', 'WALLET',
                # Abbreviations
                'CC', 'DC', 'NB', 'INTENT', 'RUPAY', 'RUPAYCREDIT',
                'BHIM_UPI_QR', 'BHIM'
            ]
            if ',' in payment_mode:
                modes = [m.strip().upper() for m in payment_mode.split(',')]
                invalid = [m for m in modes if m not in valid_modes]
                if invalid:
                    # Don't reject, just log warning - be flexible with payment modes
                    logger.warning(f"Unrecognized payment modes: {', '.join(invalid)}")
            elif payment_mode.upper() not in valid_modes:
                # Don't reject, just log warning - be flexible with payment modes
                logger.warning(f"Unrecognized payment mode: {payment_mode}")

        if errors:
            logger.warning(f"Filter validation failed: {errors}")
        else:
            logger.debug("All filters validated successfully")

        return errors