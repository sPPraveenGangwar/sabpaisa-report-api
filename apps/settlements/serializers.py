"""
Serializers for settlement app
"""
from rest_framework import serializers
from apps.transactions.models import TransactionDetail


class SettledTransactionSerializer(serializers.ModelSerializer):
    """
    Settlement-focused transaction serializer
    """
    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'paid_amount', 'settlement_amount', 'effective_settlement_amount',
            'settlement_date', 'settlement_status', 'settlement_by',
            'settlement_bank_ref', 'settlement_utr', 'trans_date',
            'payment_mode', 'status', 'convcharges', 'gst'
        ]


class SettledFilterSerializer(serializers.Serializer):
    """
    Filter serializer for settled transactions
    """
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    settlement_status = serializers.CharField(required=False)
    utr = serializers.CharField(required=False)
    client_code = serializers.CharField(required=False)
    search = serializers.CharField(required=False)


class RefundHistorySerializer(serializers.ModelSerializer):
    """
    Refund-focused transaction serializer
    """
    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'paid_amount', 'refund_amount', 'refunded_amount',
            'refund_date', 'refunded_date', 'refund_status_code',
            'refund_message', 'refund_reason', 'refund_track_id',
            'refund_initiated_on', 'refund_process_on', 'trans_date',
            'payment_mode', 'status'
        ]


class ChargebackHistorySerializer(serializers.ModelSerializer):
    """
    Chargeback-focused transaction serializer
    """
    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'paid_amount', 'charge_back_amount', 'charge_back_debit_amount',
            'charge_back_date', 'charge_back_status', 'charge_back_remarks',
            'charge_back_credit_date_to_merchant', 'is_charge_back',
            'arn', 'trans_date', 'payment_mode', 'status'
        ]


class GroupedSettlementSerializer(serializers.Serializer):
    """
    Serializer for grouped settlement data
    """
    date = serializers.DateField(required=False)
    settlement_utr = serializers.CharField(required=False)
    client_code = serializers.CharField(required=False)
    client_name = serializers.CharField(required=False)
    total_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    settlement_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    effective_amount = serializers.DecimalField(max_digits=20, decimal_places=2, required=False)


class ReconciliationSerializer(serializers.Serializer):
    """
    Serializer for reconciliation requests
    """
    date_from = serializers.DateTimeField(required=True)
    date_to = serializers.DateTimeField(required=True)
    type = serializers.ChoiceField(
        choices=['three_way', 'two_way', 'bank_gateway', 'gateway_internal'],
        default='three_way'
    )
    client_code = serializers.CharField(required=False)
    include_pending = serializers.BooleanField(default=False)
    include_failed = serializers.BooleanField(default=False)


class ReconciliationResultSerializer(serializers.Serializer):
    """
    Serializer for reconciliation results
    """
    matched = serializers.ListField(child=serializers.DictField())
    unmatched_transactions = serializers.ListField(child=serializers.DictField())
    unmatched_settlements = serializers.ListField(child=serializers.DictField())
    unmatched_bank = serializers.ListField(child=serializers.DictField())
    summary = serializers.DictField()