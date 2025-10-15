"""
Custom managers for transaction models to handle field mismatches
"""
from django.db import models
import logging

logger = logging.getLogger('apps.transactions')


class SafeTransactionManager(models.Manager):
    """
    Manager that only queries fields that exist in the database
    """

    # Core fields that should definitely exist
    SAFE_FIELDS = [
        'txn_id', 'client_code', 'client_name', 'client_txn_id',
        'trans_date', 'trans_complete_date', 'status',
        'payment_mode', 'paid_amount', 'payee_email', 'payee_mob',
        'payee_first_name', 'payee_mid_name', 'payee_lst_name',
        'pg_name', 'pg_txn_id', 'bank_txn_id',
        'is_settled', 'settlement_date', 'settlement_amount',
        'charge_back_amount', 'charge_back_date', 'charge_back_status',
        'refund_date', 'refund_message', 'refund_status_code',
        'client_id', 'resp_msg', 'sabpaisa_resp_code',
        'auth_code', 'vpa', 'channel_id', 'mapping_id'
    ]

    def get_queryset(self):
        """Return a queryset with only safe fields"""
        # Use defer() to exclude potentially problematic fields
        qs = super().get_queryset()

        # Get all model fields
        all_fields = [f.name for f in self.model._meta.get_fields()]

        # Find fields to defer (exclude from query)
        fields_to_defer = []
        for field in all_fields:
            if field not in self.SAFE_FIELDS:
                fields_to_defer.append(field)

        if fields_to_defer:
            logger.debug(f"Deferring fields from query: {fields_to_defer}")
            qs = qs.defer(*fields_to_defer)

        return qs

    def safe_all(self):
        """Get all records with only safe fields"""
        return self.get_queryset().only(*self.SAFE_FIELDS)

    def safe_filter(self, **kwargs):
        """Filter with only safe fields"""
        return self.get_queryset().only(*self.SAFE_FIELDS).filter(**kwargs)