"""
Additional models for Settlement, Refund, and Chargeback entities
based on sabpaisa2_stage_sabpaisa database schema
"""
from django.db import models


class SettlementReportEntity(models.Model):
    """
    Settlement Report Entity model
    """
    id = models.BigIntegerField(primary_key=True)
    base_url_path = models.CharField(max_length=255, null=True, blank=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.CharField(max_length=255, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    folder = models.CharField(max_length=255, null=True, blank=True)
    sub_folder = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'settlement_report_entity'
        app_label = 'transactions'

    def __str__(self):
        return f"Settlement Report {self.id} - {self.client_code}"


class RefundReportEntity(models.Model):
    """
    Refund Report Entity model
    """
    srno = models.BigIntegerField(primary_key=True)
    amount_adjust_on = models.CharField(max_length=255, null=True, blank=True)
    amount_available_to_adjust = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    money_asked_from_merchant = models.CharField(max_length=255, null=True, blank=True)
    paid_amount = models.CharField(max_length=255, null=True, blank=True)
    payee_amount = models.CharField(max_length=255, null=True, blank=True)
    payment_mode = models.CharField(max_length=255, null=True, blank=True)
    refund_initiated_on = models.CharField(max_length=255, null=True, blank=True)
    refund_process_on = models.CharField(max_length=255, null=True, blank=True)
    refund_reason = models.CharField(max_length=255, null=True, blank=True)
    refund_track_id = models.CharField(max_length=255, null=True, blank=True)
    refunded_amount = models.CharField(max_length=255, null=True, blank=True)
    trans_date = models.CharField(max_length=255, null=True, blank=True)
    txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        managed = False
        db_table = 'refund_report_entity'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['client_code']),
            models.Index(fields=['client_txn_id']),
            models.Index(fields=['txn_id']),
        ]

    def __str__(self):
        return f"Refund {self.srno} - {self.txn_id}"


class ChargebackEntity(models.Model):
    """
    Chargeback Entity model - appears to have duplicate table definitions in SQL
    Using the first occurrence structure
    """
    srno = models.BigIntegerField(primary_key=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    trans_date = models.DateTimeField(null=True, blank=True)
    payment_mode = models.CharField(max_length=255, null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    chargeback_amount = models.FloatField(null=True, blank=True)
    chargeback_date = models.DateTimeField(null=True, blank=True)
    chargeback_status = models.CharField(max_length=255, null=True, blank=True)
    chargeback_reason = models.CharField(max_length=500, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_ref_no = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'chargback_entity'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['client_code']),
            models.Index(fields=['client_txn_id']),
            models.Index(fields=['txn_id']),
            models.Index(fields=['chargeback_date']),
        ]

    def __str__(self):
        return f"Chargeback {self.srno} - {self.txn_id}"


class SettlementReport(models.Model):
    """
    Settlement Report model
    """
    id = models.BigIntegerField(primary_key=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    settlement_date = models.DateTimeField(null=True, blank=True, db_index=True)
    settlement_amount = models.FloatField(null=True, blank=True)
    settlement_status = models.CharField(max_length=255, null=True, blank=True)
    bank_ref_no = models.CharField(max_length=255, null=True, blank=True)
    utr_number = models.CharField(max_length=255, null=True, blank=True)
    transaction_count = models.IntegerField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    total_charges = models.FloatField(null=True, blank=True)
    total_gst = models.FloatField(null=True, blank=True)
    net_amount = models.FloatField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    updated_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'settlement_report'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['client_code']),
            models.Index(fields=['settlement_date']),
        ]

    def __str__(self):
        return f"Settlement Report {self.id} - {self.client_code}"


class SettlementReportDetail(models.Model):
    """
    Settlement Report Detail model - contains individual transaction details for settlement
    """
    id = models.BigIntegerField(primary_key=True)
    settlement_report_id = models.BigIntegerField(null=True, blank=True)
    txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True)
    trans_date = models.DateTimeField(null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    charges = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)
    net_amount = models.FloatField(null=True, blank=True)
    payment_mode = models.CharField(max_length=255, null=True, blank=True)
    pg_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'settlement_report_detail'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['settlement_report_id']),
            models.Index(fields=['txn_id']),
        ]

    def __str__(self):
        return f"Settlement Detail {self.id} - {self.txn_id}"


class RefundProcessEntity(models.Model):
    """
    Refund Process Entity model
    """
    srno = models.BigIntegerField(primary_key=True)
    txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    trans_date = models.DateTimeField(null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    refund_amount = models.FloatField(null=True, blank=True)
    refund_status = models.CharField(max_length=255, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reference = models.CharField(max_length=255, null=True, blank=True)
    refund_reason = models.CharField(max_length=500, null=True, blank=True)
    initiated_by = models.CharField(max_length=255, null=True, blank=True)
    initiated_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.CharField(max_length=255, null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'refund_process_entity'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['txn_id']),
            models.Index(fields=['client_code']),
            models.Index(fields=['refund_date']),
        ]

    def __str__(self):
        return f"Refund Process {self.srno} - {self.txn_id}"


class ClientDataTable(models.Model):
    """
    Client Data Table model with client/merchant configuration
    """
    client_id = models.IntegerField(primary_key=True)
    active = models.BooleanField(default=False, null=True, blank=True)
    auth_flag = models.BooleanField(default=True, null=True, blank=True)
    auth_key = models.CharField(max_length=255)
    auth_type = models.CharField(max_length=255, null=True, blank=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_contact = models.CharField(max_length=255)
    client_email = models.CharField(max_length=255, null=True, blank=True)
    auth_iv = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    client_pass = models.CharField(max_length=255)
    client_type = models.CharField(max_length=255, null=True, blank=True)
    client_user_name = models.CharField(max_length=255)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    enquiry_flag = models.BooleanField(default=False, null=True, blank=True)
    failed_ru_url = models.CharField(max_length=255)
    is_application = models.BooleanField(default=False, null=True, blank=True)
    push_api_flag = models.BooleanField(default=False, null=True, blank=True)
    push_api_url = models.CharField(max_length=255)
    refund_applicable = models.BooleanField(default=False, null=True, blank=True)
    success_ru_url = models.CharField(max_length=255)
    ui_by_pass = models.BooleanField(default=False, null=True, blank=True)
    update_date = models.DateTimeField(null=True, blank=True)
    update_by = models.CharField(max_length=255, null=True, blank=True)
    partner_bank_id = models.IntegerField(null=True, blank=True)
    client_logo_path = models.CharField(max_length=255)
    login_id = models.IntegerField(null=True, blank=True)
    client_address = models.CharField(max_length=255, null=True, blank=True)
    applicable_for_challan = models.CharField(max_length=45, null=True, blank=True)

    # Legacy duplicate fields with different casing
    application_appId = models.IntegerField(null=True, blank=True)
    authFlag = models.CharField(max_length=255, null=True, blank=True)
    authType = models.CharField(max_length=255, null=True, blank=True)
    bankClientParam = models.CharField(max_length=45, null=True, blank=True)
    bypassOptionsFlag = models.CharField(max_length=255, null=True, blank=True)
    clientCode = models.CharField(max_length=255, null=True, blank=True)
    clientContact = models.CharField(max_length=255, null=True, blank=True)
    clientEmail = models.CharField(max_length=255, null=True, blank=True)
    clientIV = models.CharField(max_length=255, null=True, blank=True)
    clientKey = models.CharField(max_length=255, null=True, blank=True)
    clientName = models.CharField(max_length=255, null=True, blank=True)
    clientPass = models.CharField(max_length=255, null=True, blank=True)
    clientTypeId = models.IntegerField(null=True, blank=True)
    clientUsername = models.CharField(max_length=255, null=True, blank=True)
    failureReturnURL = models.CharField(max_length=255, null=True, blank=True)
    isApplication = models.IntegerField(null=True, blank=True)
    is_refund_applicable = models.CharField(max_length=255, null=True, blank=True)
    loginBean_loginId = models.IntegerField(null=True, blank=True)
    redirect_to_new_layout = models.CharField(max_length=255, null=True, blank=True)
    sendPaymentRetrievalNotification = models.CharField(max_length=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'client_data_table'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['client_code']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f"{self.client_code} - {self.client_name}"


class MerchantWhitelist(models.Model):
    """
    Merchant Whitelist model for IP/domain whitelisting
    """
    merchant_whitelist_id = models.IntegerField(primary_key=True)
    active = models.BooleanField(null=True, blank=True)
    white_list = models.CharField(max_length=255, null=True, blank=True)
    client_id = models.IntegerField(db_index=True)

    class Meta:
        managed = False
        db_table = 'merchant_whitelist'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f"Whitelist {self.merchant_whitelist_id} - Client {self.client_id}"


class UserZoneMapper(models.Model):
    """
    User Zone Mapper model - maps users to zones/regions
    Note: This table structure needs to be verified from database
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    zone_id = models.IntegerField(null=True, blank=True, db_index=True)
    zone_name = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'user_zone_mapper'  # Verify actual table name
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['zone_id']),
        ]

    def __str__(self):
        return f"User {self.user_id} - Zone {self.zone_name}"