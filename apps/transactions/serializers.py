"""
Serializers for transaction app - updated to match accurate models
"""
from rest_framework import serializers
from .models import (
    TransactionDetail,
    ClientRequestTempStore,
    SettlementReportEntity,
    RefundReportEntity,
    ChargebackEntity,
    SettlementReport,
    SettlementReportDetail,
    RefundProcessEntity,
    MerchantWhitelist,
    ClientDataTable,
    UserZoneMapper
)
from django.db.models import Sum, Count, Avg


class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive transaction detail serializer with safe database fields
    """
    # Add computed fields
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        # List only fields that are confirmed to exist in the database
        fields = [
            'txn_id', 'act_amount', 'pg_name', 'pg_pay_mode', 'pg_response_code',
            'pg_return_amount', 'pg_txn_id', 'alert_flag', 'amount_type',
            'application_fail_url', 'application_succ_url', 'auth_code',
            'bank_txn_id', 'challan_no', 'changed_on_followup', 'client_id',
            'client_name', 'client_request_ip', 'convcharges', 'ep_charges',
            'enquiry_counter', 'enquiry_date', 'gst', 'mapping_id',
            'paid_amount', 'payee_amount', 'payee_email', 'payee_first_name',
            'payee_lst_name', 'payee_mid_name', 'payee_mob', 'payment_mode',
            'program_id', 'refund_date', 'refund_message', 'refund_status_code',
            'reg_number', 'resp_msg', 'sabpaisa_resp_code', 'status',
            'trans_complete_date', 'trans_date', 'client_code', 'client_txn_id',
            'uit_application_id', 'vpa', 'vpa_remarks', 'is_settled',
            'pag_response_code', 'charge_back_amount', 'charge_back_date',
            'charge_back_status', 'settlement_date', 'settlement_amount',
            'channel_id', 'donation_amount', 'card_brand', 'device_name',
            'bank_message', 'fee_forward', 'payer_confirmation',
            'refunded_date', 'settlement_status', 'settlement_by',
            'settlement_bank_ref', 'settlement_remarks', 'settlement_utr',
            'refund_request_from', 'chargeback_request_from', 'udf19',
            'ep_conv_rate', 'ep_conv_rate_type', 'gst_rate', 'gst_rate_type',
            'sp_conv_rate', 'sp_conv_rate_type', 'bank_errorcode',
            'sabpaisa_errorcode', 'terminal_status', 'bin_update_flag',
            'force_success_flag', 'conv_gst', 'endpoint_gst', 'endpoint_id',
            'payment_mode_id', 'broser_name', 'broser_details',
            'browser_details', 'business_ctg_id', 'referral_id',
            'service_prt_bnk_id', 'udf_Extra', 'udf20', 'trans_push_date',
            'payee_name'  # Include computed field
        ]

    def get_payee_name(self, obj):
        """Use the model's payee_name property"""
        return obj.payee_name


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for transaction lists
    """
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'payee_name', 'payee_email', 'payee_mob',
            'pg_name', 'pg_txn_id', 'bank_txn_id', 'is_settled',
            'settlement_date', 'settlement_amount'
        ]

    def get_payee_name(self, obj):
        return obj.payee_name


class ClientRequestTempStoreSerializer(serializers.ModelSerializer):
    """
    Serializer for client request temp store
    """
    payee_full_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ClientRequestTempStore
        fields = '__all__'

    def get_payee_full_name(self, obj):
        return obj.payee_full_name

    def get_full_name(self, obj):
        return obj.full_name


class SettlementReportEntitySerializer(serializers.ModelSerializer):
    """
    Serializer for settlement report entity
    """
    class Meta:
        model = SettlementReportEntity
        fields = '__all__'


class RefundReportEntitySerializer(serializers.ModelSerializer):
    """
    Serializer for refund report entity
    """
    class Meta:
        model = RefundReportEntity
        fields = '__all__'


class ChargebackEntitySerializer(serializers.ModelSerializer):
    """
    Serializer for chargeback entity
    """
    class Meta:
        model = ChargebackEntity
        fields = '__all__'


class SettlementReportSerializer(serializers.ModelSerializer):
    """
    Serializer for settlement report
    """
    class Meta:
        model = SettlementReport
        fields = '__all__'


class SettlementReportDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for settlement report details
    """
    class Meta:
        model = SettlementReportDetail
        fields = '__all__'


class RefundProcessEntitySerializer(serializers.ModelSerializer):
    """
    Serializer for refund process entity
    """
    class Meta:
        model = RefundProcessEntity
        fields = '__all__'


class TransactionSearchRequestSerializer(serializers.Serializer):
    """
    Serializer for transaction search requests
    """
    # CASE 1: Merchant-wise filtering
    client_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of merchant client codes"
    )

    # CASE 2: Date filtering
    date_filter = serializers.ChoiceField(
        choices=['today', 'yesterday', 'week', 'month', 'custom'],
        required=False
    )
    from_date = serializers.DateField(
        required=False,
        format="%Y-%m-%d",
        help_text="Start date for custom range (YYYY-MM-DD)"
    )
    to_date = serializers.DateField(
        required=False,
        format="%Y-%m-%d",
        help_text="End date for custom range (YYYY-MM-DD)"
    )

    # CASE 3: Payment mode filtering
    payment_modes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of payment modes"
    )

    # CASE 4: Status filtering
    status = serializers.ChoiceField(
        choices=['SUCCESS', 'FAILED', 'PENDING', 'all'],
        required=False,
        default='all'
    )

    # CASE 5: Amount range filtering
    min_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Minimum transaction amount"
    )
    max_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Maximum transaction amount"
    )

    # CASE 6: Transaction ID search
    txn_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of transaction IDs"
    )
    client_txn_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of client transaction IDs"
    )

    # Pagination
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)

    # Export format
    export_format = serializers.ChoiceField(
        choices=['json', 'csv', 'excel'],
        default='json',
        required=False
    )


class SettlementSerializer(serializers.ModelSerializer):
    """
    Settlement transaction serializer
    """
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status',
            'payment_mode', 'paid_amount', 'payee_name',
            'is_settled', 'settlement_date', 'settlement_amount',
            'settlement_status', 'settlement_by', 'settlement_bank_ref',
            'settlement_remarks', 'settlement_utr',
            'convcharges', 'ep_charges', 'gst',
            'pg_name', 'bank_txn_id'
        ]

    def get_payee_name(self, obj):
        return obj.payee_name


class RefundSerializer(serializers.ModelSerializer):
    """
    Refund transaction serializer
    """
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'status', 'payment_mode', 'paid_amount',
            'payee_name', 'refund_date', 'refunded_date',
            'refund_message', 'refund_status_code',
            'refund_request_from', 'pg_name', 'bank_txn_id'
        ]

    def get_payee_name(self, obj):
        return obj.payee_name


class ChargebackSerializer(serializers.ModelSerializer):
    """
    Chargeback transaction serializer
    """
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'status', 'payment_mode', 'paid_amount',
            'payee_name', 'charge_back_amount', 'charge_back_date',
            'charge_back_status', 'chargeback_request_from',
            'pg_name', 'bank_txn_id'
        ]

    def get_payee_name(self, obj):
        return obj.payee_name


class TransactionSummarySerializer(serializers.Serializer):
    """
    Transaction summary/analytics serializer
    """
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    successful_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_transaction_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Payment mode breakdown
    payment_mode_summary = serializers.ListField(
        child=serializers.DictField()
    )

    # Date range
    from_date = serializers.DateField()
    to_date = serializers.DateField()

    # Client summary
    client_summary = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class PaymentModeSummarySerializer(serializers.Serializer):
    """
    Payment mode summary serializer
    """
    payment_mode = serializers.CharField()
    transaction_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    success_rate = serializers.FloatField()


class ClientSummarySerializer(serializers.Serializer):
    """
    Client-wise summary serializer
    """
    client_code = serializers.CharField()
    client_name = serializers.CharField()
    transaction_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    success_rate = serializers.FloatField()


# Additional serializers for compatibility with views
class TransactionWholeSerializer(TransactionDetailSerializer):
    """
    Serializer for whole transaction details - alias for TransactionDetailSerializer
    """
    pass


class MerchantTransactionFilterSerializer(TransactionSearchRequestSerializer):
    """
    Serializer for merchant transaction filtering
    """
    pass


class AdminTransactionFilterSerializer(TransactionSearchRequestSerializer):
    """
    Serializer for admin transaction filtering
    """
    # Admin can see all merchants
    view_all_merchants = serializers.BooleanField(default=True, required=False)


class SettlementTransactionSerializer(SettlementSerializer):
    """
    Alias for SettlementSerializer for compatibility
    """
    pass


class RefundTransactionSerializer(RefundSerializer):
    """
    Alias for RefundSerializer for compatibility
    """
    pass


class ChargebackTransactionSerializer(ChargebackSerializer):
    """
    Alias for ChargebackSerializer for compatibility
    """
    pass


class DOITCTransactionSerializer(serializers.ModelSerializer):
    """
    DOITC specific transaction serializer
    """
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'status', 'payment_mode', 'paid_amount',
            'payee_name', 'pg_name', 'bank_txn_id',
            'is_settled', 'settlement_date'
        ]

    def get_payee_name(self, obj):
        return obj.payee_name


class SBICardDataSerializer(serializers.ModelSerializer):
    """
    SBI Card specific data serializer
    """
    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'trans_date', 'paid_amount',
            'card_brand', 'bank_txn_id', 'auth_code',
            'status', 'pg_name'
        ]


class SuccessRateAnalyticsSerializer(serializers.Serializer):
    """
    Success rate analytics serializer
    """
    date = serializers.DateField()
    total_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    success_rate = serializers.FloatField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)


class MerchantWhitelistSerializer(serializers.ModelSerializer):
    """
    Merchant whitelist serializer
    """
    class Meta:
        model = MerchantWhitelist
        fields = '__all__'


class TransactionExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting transactions
    """
    payee_name = serializers.SerializerMethodField()

    class Meta:
        model = TransactionDetail
        fields = [
            'txn_id', 'client_txn_id', 'client_code', 'client_name',
            'trans_date', 'trans_complete_date', 'status', 'payment_mode',
            'paid_amount', 'payee_name', 'payee_email', 'payee_mob',
            'pg_name', 'pg_txn_id', 'bank_txn_id',
            'convcharges', 'ep_charges', 'gst',
            'is_settled', 'settlement_date', 'settlement_amount',
            'refund_date', 'refund_status_code',
            'charge_back_amount', 'charge_back_date', 'charge_back_status'
        ]

    def get_payee_name(self, obj):
        return obj.payee_name