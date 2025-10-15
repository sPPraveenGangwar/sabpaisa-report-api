"""
Aggregation models for pre-calculated statistics
Handles 100K+ daily transactions efficiently with materialized views
"""
from django.db import models
from django.utils import timezone


class DailyTransactionSummary(models.Model):
    """
    Daily aggregated transaction statistics per merchant
    Updated in real-time or via scheduled tasks
    """
    date = models.DateField(db_index=True)
    client_code = models.CharField(max_length=255, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)

    # Transaction counts
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)

    # Amount aggregations
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    success_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    failed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Settlement info
    settled_count = models.IntegerField(default=0)
    settled_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    unsettled_count = models.IntegerField(default=0)
    unsettled_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Refund info
    refund_count = models.IntegerField(default=0)
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Chargeback info
    chargeback_count = models.IntegerField(default=0)
    chargeback_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'daily_transaction_summary'
        unique_together = ('date', 'client_code')
        indexes = [
            models.Index(fields=['date', 'client_code']),
            models.Index(fields=['client_code', 'date']),
            models.Index(fields=['-date']),  # Most recent first
        ]
        ordering = ['-date', 'client_code']

    def __str__(self):
        return f"{self.client_code} - {self.date}"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_count == 0:
            return 0
        return (self.success_count / self.total_count) * 100

    @property
    def settlement_rate(self):
        """Calculate settlement rate percentage"""
        if self.success_count == 0:
            return 0
        return (self.settled_count / self.success_count) * 100


class PaymentModeSummary(models.Model):
    """
    Daily payment mode wise statistics
    """
    date = models.DateField(db_index=True)
    client_code = models.CharField(max_length=255, db_index=True)
    payment_mode = models.CharField(max_length=255, db_index=True)

    # Counts
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    # Amounts
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    success_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Average transaction value
    avg_transaction_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_mode_summary'
        unique_together = ('date', 'client_code', 'payment_mode')
        indexes = [
            models.Index(fields=['date', 'payment_mode']),
            models.Index(fields=['client_code', 'date', 'payment_mode']),
        ]
        ordering = ['-date', 'payment_mode']

    def __str__(self):
        return f"{self.payment_mode} - {self.date}"


class HourlyTransactionStats(models.Model):
    """
    Hourly transaction statistics for real-time dashboards
    Useful for monitoring current day performance
    """
    date = models.DateField(db_index=True)
    hour = models.IntegerField(db_index=True)  # 0-23
    client_code = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    # Counts
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    # Amounts
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    success_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hourly_transaction_stats'
        unique_together = ('date', 'hour', 'client_code')
        indexes = [
            models.Index(fields=['date', 'hour']),
            models.Index(fields=['client_code', 'date', 'hour']),
        ]
        ordering = ['-date', '-hour']

    def __str__(self):
        return f"{self.date} {self.hour}:00"


class MerchantMonthlyStats(models.Model):
    """
    Monthly statistics per merchant for long-term trends
    Pre-calculated to avoid scanning millions of records
    """
    year = models.IntegerField(db_index=True)
    month = models.IntegerField(db_index=True)  # 1-12
    client_code = models.CharField(max_length=255, db_index=True)

    # Transaction counts
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    # Amounts
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    success_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # Settlement
    settled_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    pending_settlement = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # Unique customers
    unique_customers = models.IntegerField(default=0)

    # Average order value
    average_transaction_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'merchant_monthly_stats'
        unique_together = ('year', 'month', 'client_code')
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['client_code', 'year', 'month']),
        ]
        ordering = ['-year', '-month', 'client_code']

    def __str__(self):
        return f"{self.client_code} - {self.year}/{self.month:02d}"


class TransactionSearchCache(models.Model):
    """
    Cache for frequently accessed transaction searches
    Stores query hash and results for quick retrieval
    """
    query_hash = models.CharField(max_length=64, unique=True, db_index=True)
    query_params = models.JSONField()  # Store original query parameters

    # Cached results
    result_count = models.IntegerField()
    result_summary = models.JSONField()  # Summary statistics

    # Cache metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    hit_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'transaction_search_cache'
        indexes = [
            models.Index(fields=['query_hash', 'expires_at']),
            models.Index(fields=['expires_at']),  # For cleanup
        ]

    def __str__(self):
        return f"Cache: {self.query_hash[:8]}..."

    def is_valid(self):
        """Check if cache entry is still valid"""
        return timezone.now() < self.expires_at

    def increment_hit(self):
        """Increment cache hit counter"""
        self.hit_count += 1
        self.save(update_fields=['hit_count'])
