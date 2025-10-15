"""
Transaction models for payment processing and reporting
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal
from .managers import SafeTransactionManager


class TransactionDetail(models.Model):
    """
    Main transaction table from sabpaisa2_stage_sabpaisa database
    Contains 100+ fields for comprehensive transaction tracking
    """
    # Primary identifier
    txn_id = models.CharField(max_length=255, primary_key=True)

    # Core transaction fields
    act_amount = models.FloatField(null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    payee_amount = models.FloatField(null=True, blank=True)
    settlement_amount = models.FloatField(null=True, blank=True)
    refund_amount = models.FloatField(null=True, blank=True)
    refunded_amount = models.FloatField(null=True, blank=True)

    # Payment gateway fields
    pg_name = models.CharField(max_length=255, null=True, blank=True)
    pg_pay_mode = models.CharField(max_length=255, null=True, blank=True)
    pg_response_code = models.CharField(max_length=255, null=True, blank=True)
    pg_return_amount = models.FloatField(null=True, blank=True)
    pg_txn_id = models.CharField(max_length=255, null=True, blank=True)
    pag_response_code = models.CharField(max_length=255, null=True, blank=True)

    # Client/Merchant information
    client_id = models.IntegerField(null=True, blank=True, db_index=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_request_ip = models.CharField(max_length=255, null=True, blank=True)

    # Payee information
    payee_email = models.CharField(max_length=255, null=True, blank=True)
    payee_first_name = models.CharField(max_length=255, null=True, blank=True)
    payee_lst_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mid_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mob = models.CharField(max_length=255, null=True, blank=True)

    # Transaction status and dates
    status = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    trans_date = models.DateTimeField(db_index=True)
    trans_complete_date = models.DateTimeField(null=True, blank=True)
    trans_push_date = models.DateTimeField(null=True, blank=True)

    # Settlement fields
    is_settled = models.BooleanField(null=True, blank=True, db_index=True)
    settlement_date = models.DateTimeField(null=True, blank=True, db_index=True)
    settlement_status = models.CharField(max_length=255, null=True, blank=True)
    settlement_by = models.CharField(max_length=255, null=True, blank=True)
    settlement_bank_ref = models.CharField(max_length=150, null=True, blank=True)
    settlement_remarks = models.CharField(max_length=150, null=True, blank=True)
    settlement_utr = models.CharField(max_length=150, null=True, blank=True)
    settlement_bank_amount = models.FloatField(null=True, blank=True)
    effective_settlement_amount = models.FloatField(null=True, blank=True)

    # Refund fields
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_message = models.CharField(max_length=255, null=True, blank=True)
    refund_status_code = models.CharField(max_length=255, null=True, blank=True)
    refund_initiated_on = models.DateTimeField(null=True, blank=True)
    refund_process_on = models.DateTimeField(null=True, blank=True)
    refund_reason = models.CharField(max_length=200, null=True, blank=True)
    refund_track_id = models.CharField(max_length=50, null=True, blank=True)
    refund_request_from = models.CharField(max_length=255, null=True, blank=True)
    refunded_date = models.DateTimeField(null=True, blank=True)

    # Chargeback fields
    charge_back_amount = models.FloatField(null=True, blank=True)
    charge_back_date = models.DateTimeField(null=True, blank=True)
    charge_back_status = models.CharField(max_length=255, null=True, blank=True)
    charge_back_debit_amount = models.FloatField(null=True, blank=True)
    charge_back_credit_date_to_merchant = models.DateTimeField(null=True, blank=True)
    charge_back_remarks = models.CharField(max_length=200, null=True, blank=True)
    chargeback_request_from = models.CharField(max_length=255, null=True, blank=True)
    is_charge_back = models.BooleanField(null=True, blank=True)

    # Bank and payment details
    bank_txn_id = models.CharField(max_length=255, null=True, blank=True)
    # bank_message = models.CharField(max_length=255, null=True, blank=True)  # Not in actual DB
    # bank_message1 = models.CharField(max_length=500, null=True, blank=True)  # Not in actual DB
    # bank_errorcode = models.CharField(max_length=255, null=True, blank=True, default='NA')  # Not in actual DB
    # bank_name = models.CharField(max_length=50, null=True, blank=True)  # Not in actual DB
    payment_mode = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    payment_mode_id = models.IntegerField(null=True, blank=True)

    # Additional transaction details
    challan_no = models.CharField(max_length=255, null=True, blank=True)
    auth_code = models.CharField(max_length=255, null=True, blank=True)
    vpa = models.CharField(max_length=255, null=True, blank=True)
    vpa_remarks = models.CharField(max_length=255, null=True, blank=True)
    arn = models.CharField(max_length=50, null=True, blank=True)
    card_brand = models.CharField(max_length=255, null=True, blank=True, default='NA')

    # Charges and fees
    convcharges = models.FloatField(null=True, blank=True)
    conv_gst = models.FloatField(null=True, blank=True)
    ep_charges = models.FloatField(null=True, blank=True)
    endpoint_gst = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)
    ep_conv_rate = models.FloatField(null=True, blank=True)
    ep_conv_rate_type = models.CharField(max_length=10, null=True, blank=True)
    gst_rate = models.FloatField(null=True, blank=True)
    gst_rate_type = models.CharField(max_length=10, null=True, blank=True)
    sp_conv_rate = models.FloatField(null=True, blank=True)
    sp_conv_rate_type = models.CharField(max_length=10, null=True, blank=True)

    # URLs and application data
    application_fail_url = models.CharField(max_length=255, null=True, blank=True)
    application_succ_url = models.CharField(max_length=255, null=True, blank=True)

    # Response and status messages
    resp_msg = models.CharField(max_length=255, null=True, blank=True)
    sabpaisa_resp_code = models.CharField(max_length=255, null=True, blank=True)
    sabpaisa_errorcode = models.CharField(max_length=255, null=True, blank=True, default='NA')

    # Flags
    alert_flag = models.CharField(max_length=255, null=True, blank=True)
    force_success_flag = models.BooleanField(null=True, blank=True, default=False)
    trans_flag = models.BooleanField(null=True, blank=True)
    trans_push_flag = models.BooleanField(null=True, blank=True)
    payer_confirmation = models.BooleanField(null=True, blank=True)
    bin_update_flag = models.BooleanField(null=True, blank=True, default=False)
    mandate_flag = models.BooleanField(null=True, blank=True, default=False)

    # Business categorization - commented out due to database mismatch
    # business_ctg_id = models.IntegerField(null=True, blank=True)
    # business_ctg_code = models.CharField(max_length=50, null=True, blank=True)
    # referral_id = models.IntegerField(null=True, blank=True)
    # referral_code = models.CharField(max_length=50, null=True, blank=True)

    # Additional metadata
    program_id = models.CharField(max_length=255, null=True, blank=True)
    mapping_id = models.IntegerField(null=True, blank=True)
    endpoint_id = models.IntegerField(null=True, blank=True)
    channel_id = models.CharField(max_length=255, null=True, blank=True)

    # Browser and device details
    browser_details = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)

    # Tracking fields
    enquiry_counter = models.IntegerField(null=True, blank=True, default=0)
    enquiry_date = models.DateTimeField(null=True, blank=True)
    trans_updated_by = models.CharField(max_length=100, null=True, blank=True)
    transaction_tracker_id = models.IntegerField(null=True, blank=True, default=1)
    transaction_tracker_time = models.DateTimeField(null=True, blank=True)

    # UDF fields (User Defined Fields) - only including udf19 and udf20 as per SQL
    udf19 = models.CharField(max_length=255, null=True, blank=True)
    udf20 = models.CharField(max_length=255, null=True, blank=True)

    # Mandate related fields
    mandate_charges = models.FloatField(null=True, blank=True)
    mandate_status = models.CharField(max_length=20, null=True, blank=True)
    mandate_conv_charges = models.FloatField(null=True, blank=True)
    mandate_down_payment = models.FloatField(null=True, blank=True)
    mandate_ep_charges = models.FloatField(null=True, blank=True)
    mandate_gst_charges = models.FloatField(null=True, blank=True)

    # Additional fields
    amount_type = models.CharField(max_length=255, null=True, blank=True)
    fee_forward = models.CharField(max_length=255, null=True, blank=True)
    donation_amount = models.FloatField(null=True, blank=True, default=0)
    terminal_status = models.CharField(max_length=50, null=True, blank=True)
    value_date = models.DateTimeField(null=True, blank=True)

    # Rolling reserve fields
    rolling_reserve_plus = models.FloatField(null=True, blank=True)
    rolling_reserve_minus = models.FloatField(null=True, blank=True)

    # Add safe manager
    objects = models.Manager()  # Default manager
    safe_objects = SafeTransactionManager()  # Safe manager that excludes problematic fields

    class Meta:
        managed = False  # IMPORTANT: Don't let Django create/modify this table
        db_table = 'transaction_detail'
        app_label = 'transactions'

    def __str__(self):
        return f"{self.txn_id} - {self.client_name} - {self.status}"


class ClientDataTable(models.Model):
    """
    Client/Merchant master data from sabpaisa2_stage_sabpaisa
    """
    client_id = models.IntegerField(primary_key=True)
    active = models.BooleanField(default=False)
    auth_flag = models.BooleanField(default=True)
    auth_key = models.CharField(max_length=255)
    auth_iv = models.CharField(max_length=255)
    auth_type = models.CharField(max_length=255, null=True, blank=True)

    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255)
    client_contact = models.CharField(max_length=255)
    client_email = models.CharField(max_length=255, null=True, blank=True)
    client_pass = models.CharField(max_length=255)
    client_user_name = models.CharField(max_length=255)
    client_type = models.CharField(max_length=255, null=True, blank=True)
    client_address = models.CharField(max_length=255, null=True, blank=True)
    client_logo_path = models.CharField(max_length=255)
    client_mcc = models.CharField(max_length=255, null=True, blank=True)

    # Flags
    enquiry_flag = models.BooleanField(default=False)
    is_application = models.BooleanField(default=False)
    push_api_flag = models.BooleanField(default=False)
    refund_applicable = models.BooleanField(default=False)
    ui_by_pass = models.BooleanField(default=False)
    duplicate_restriction = models.BooleanField(default=False)
    donation_flag = models.BooleanField(default=False)
    round_off = models.BooleanField(default=True)
    van_flag = models.BooleanField(default=False)
    tpv_flag = models.BooleanField(default=False)
    abort_job_flag = models.BooleanField(default=False)
    gift_card_flag = models.BooleanField(default=False)
    is_client_logo_flag = models.BooleanField(default=False)
    is_commercial_flag = models.BooleanField(default=False)
    is_partnerbank_logo_flag = models.BooleanField(default=False)
    is_whitelisted = models.BooleanField(default=False)
    is_vpa_verify = models.BooleanField(default=False)
    force_success_flag = models.BooleanField(default=False)
    checkout_cancel_btn = models.BooleanField(default=False)
    client_alert_flag = models.BooleanField(default=True)
    client_disable_flag = models.BooleanField(default=False)
    mandate_flag = models.BooleanField(default=False)
    is_unicode_allowed = models.BooleanField(default=False)

    # URLs
    push_api_url = models.CharField(max_length=255)
    failed_ru_url = models.CharField(max_length=255)
    success_ru_url = models.CharField(max_length=255)

    # Additional fields
    created_by = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(null=True, blank=True)
    update_by = models.CharField(max_length=255, null=True, blank=True)

    partner_bank_id = models.IntegerField(null=True, blank=True)
    login_id = models.IntegerField(null=True, blank=True)
    risk_category = models.IntegerField(null=True, blank=True)
    api_version = models.IntegerField(default=0)

    # Business categorization
    business_ctg_id = models.IntegerField(null=True, blank=True)
    business_ctg_code = models.CharField(max_length=255, null=True, blank=True)
    referral_id = models.IntegerField(null=True, blank=True)
    referral_code = models.CharField(max_length=255, null=True, blank=True)

    # Alert messages
    client_alert_message = models.CharField(max_length=255, null=True, blank=True)
    client_disable_message = models.CharField(max_length=255, null=True, blank=True)

    # Mandate fields
    mandate_amount = models.FloatField(null=True, blank=True)
    mandate_charges = models.FloatField(null=True, blank=True)

    # Refund configuration
    refund_type = models.CharField(max_length=255, null=True, blank=True)
    refund_day = models.IntegerField(null=True, blank=True)

    master_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'client_data_table'
        app_label = 'transactions'

    def __str__(self):
        return f"{self.client_code} - {self.client_name}"


class ClientRequestTempStore(models.Model):
    """
    Temporary storage for client transaction requests
    """
    req_id = models.AutoField(primary_key=True)
    txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True)

    # Request data
    request_data = models.TextField(null=True, blank=True)
    response_data = models.TextField(null=True, blank=True)

    # Transaction details
    amount = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    # Payee info
    payee_name = models.CharField(max_length=255, null=True, blank=True)
    payee_email = models.CharField(max_length=255, null=True, blank=True)
    payee_mobile = models.CharField(max_length=20, null=True, blank=True)

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Additional fields
    payment_mode = models.CharField(max_length=50, null=True, blank=True)
    callback_url = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'client_request_temp_store'
        app_label = 'transactions'

    def __str__(self):
        return f"{self.req_id} - {self.txn_id}"


class UserZoneMapper(models.Model):
    """
    Maps users to zones for geographic access control
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(db_index=True)
    zone_code = models.CharField(max_length=50)
    zone_name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'user_zone_mapper'
        app_label = 'transactions'

    def __str__(self):
        return f"User {self.user_id} - Zone {self.zone_code}"


class MerchantWhitelist(models.Model):
    """
    Merchant whitelist for enhanced security
    """
    id = models.AutoField(primary_key=True)
    client_code = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'merchant_whitelist'
        app_label = 'transactions'
        unique_together = [['client_code', 'ip_address', 'domain']]

    def __str__(self):
        return f"{self.client_code} - {self.ip_address or self.domain}"