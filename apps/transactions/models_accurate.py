"""
Accurate TransactionDetail and ClientRequestTempStore models
based on exact sabpaisa2_stage_sabpaisa database schema
"""
from django.db import models


class TransactionDetail(models.Model):
    """
    Transaction Detail model with exact fields from database
    """
    # Primary key
    txn_id = models.CharField(max_length=255, primary_key=True)

    # Amount fields
    act_amount = models.FloatField(null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    payee_amount = models.FloatField(null=True, blank=True)
    donation_amount = models.FloatField(default=0, null=True, blank=True)

    # Payment gateway fields
    pg_name = models.CharField(max_length=255, null=True, blank=True)
    pg_pay_mode = models.CharField(max_length=255, null=True, blank=True)
    pg_response_code = models.CharField(max_length=255, null=True, blank=True)
    pg_return_amount = models.FloatField(null=True, blank=True)
    pg_txn_id = models.CharField(max_length=255, null=True, blank=True)

    # Status and flags
    alert_flag = models.CharField(max_length=255, null=True, blank=True)
    amount_type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # URLs
    application_fail_url = models.CharField(max_length=255, null=True, blank=True)
    application_succ_url = models.CharField(max_length=255, null=True, blank=True)

    # Bank fields
    auth_code = models.CharField(max_length=255, null=True, blank=True)
    bank_txn_id = models.CharField(max_length=255, null=True, blank=True)
    bank_message = models.CharField(max_length=255, null=True, blank=True)
    bank_message1 = models.CharField(max_length=500, null=True, blank=True)
    bank_errorcode = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Challan
    challan_no = models.CharField(max_length=255, null=True, blank=True)
    changed_on_followup = models.CharField(max_length=255, null=True, blank=True)

    # Client information
    client_id = models.IntegerField(null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_request_ip = models.CharField(max_length=255, null=True, blank=True)

    # Charges and fees
    convcharges = models.FloatField(null=True, blank=True)
    ep_charges = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)
    conv_gst = models.FloatField(null=True, blank=True)
    endpoint_gst = models.FloatField(null=True, blank=True)

    # Enquiry fields
    enquiry_counter = models.IntegerField(default=0, null=True, blank=True)
    enquiry_date = models.DateTimeField(null=True, blank=True)

    # Mapping
    mapping_id = models.IntegerField(null=True, blank=True)

    # Payee information
    payee_email = models.CharField(max_length=255, null=True, blank=True)
    payee_first_name = models.CharField(max_length=255, null=True, blank=True)
    payee_lst_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mid_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mob = models.CharField(max_length=255, null=True, blank=True)

    # Payment mode and program
    payment_mode = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    payment_mode_id = models.IntegerField(null=True, blank=True)
    program_id = models.CharField(max_length=255, null=True, blank=True)

    # Refund fields
    refund_date = models.DateTimeField(null=True, blank=True)
    refunded_date = models.DateTimeField(null=True, blank=True)
    refund_message = models.CharField(max_length=255, null=True, blank=True)
    refund_status_code = models.CharField(max_length=255, null=True, blank=True)
    refund_request_from = models.CharField(max_length=255, null=True, blank=True)

    # Registration and response
    reg_number = models.CharField(max_length=255, null=True, blank=True)
    resp_msg = models.CharField(max_length=255, null=True, blank=True)
    sabpaisa_resp_code = models.CharField(max_length=255, null=True, blank=True)
    sabpaisa_errorcode = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Transaction dates
    trans_complete_date = models.DateTimeField(null=True, blank=True)
    trans_date = models.DateTimeField(db_index=True)
    trans_push_date = models.DateTimeField(null=True, blank=True)

    # UIT and VPA
    uit_application_id = models.CharField(max_length=255, null=True, blank=True)
    vpa = models.CharField(max_length=255, null=True, blank=True)
    vpa_remarks = models.CharField(max_length=255, null=True, blank=True)

    # Settlement fields
    is_settled = models.BooleanField(null=True, blank=True, db_index=True)
    settlement_date = models.DateTimeField(null=True, blank=True, db_index=True)
    settlement_amount = models.FloatField(null=True, blank=True)
    settlement_status = models.CharField(max_length=255, null=True, blank=True)
    settlement_by = models.CharField(max_length=255, null=True, blank=True)
    settlement_bank_ref = models.CharField(max_length=150, null=True, blank=True)
    settlement_remarks = models.CharField(max_length=150, null=True, blank=True)
    settlement_utr = models.CharField(max_length=150, null=True, blank=True)

    # PAG response
    pag_response_code = models.CharField(max_length=255, null=True, blank=True)

    # Chargeback fields
    charge_back_amount = models.FloatField(null=True, blank=True)
    charge_back_date = models.DateTimeField(null=True, blank=True)
    charge_back_status = models.CharField(max_length=255, null=True, blank=True)
    chargeback_request_from = models.CharField(max_length=255, null=True, blank=True)

    # Channel
    channel_id = models.CharField(max_length=255, null=True, blank=True)

    # Browser and device
    broser_name = models.CharField(max_length=255, null=True, blank=True)
    broser_details = models.CharField(max_length=255, null=True, blank=True)
    browser_details = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)

    # UDF fields
    udf_Extra = models.CharField(max_length=255, null=True, blank=True)
    udf19 = models.CharField(max_length=255, null=True, blank=True)
    udf20 = models.CharField(max_length=255, null=True, blank=True)

    # Card details
    card_brand = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Fee forward
    fee_forward = models.CharField(max_length=255, null=True, blank=True)

    # Payer confirmation
    payer_confirmation = models.BooleanField(null=True, blank=True)
    sent_notification_payer_confirmation_dt = models.DateTimeField(null=True, blank=True)
    sent_notification_payer_confirmation_url = models.CharField(max_length=255, null=True, blank=True)
    payer_confirmation_respones = models.CharField(max_length=255, null=True, blank=True)
    payer_confirmation_respones_dt = models.DateTimeField(null=True, blank=True)
    payer_confirmation_request_ct = models.IntegerField(null=True, blank=True)

    # Rates
    ep_conv_rate = models.FloatField(null=True, blank=True)
    ep_conv_rate_type = models.CharField(max_length=10, null=True, blank=True)
    gst_rate = models.FloatField(null=True, blank=True)
    gst_rate_type = models.CharField(max_length=10, null=True, blank=True)
    sp_conv_rate = models.FloatField(null=True, blank=True)
    sp_conv_rate_type = models.CharField(max_length=10, null=True, blank=True)

    # Terminal and flags
    terminal_status = models.CharField(max_length=50, null=True, blank=True)
    bin_update_flag = models.BooleanField(default=False, null=True, blank=True)
    force_success_flag = models.BooleanField(default=False, null=True, blank=True)

    # IDs
    endpoint_id = models.IntegerField(null=True, blank=True)
    business_ctg_id = models.IntegerField(null=True, blank=True)
    referral_id = models.IntegerField(null=True, blank=True)
    service_prt_bnk_id = models.IntegerField(null=True, blank=True)

    # Duplicate fields with different case (legacy compatibility)
    # These are duplicate columns with different naming conventions
    actAmount = models.FloatField(null=True, blank=True)
    agrProfitshare = models.FloatField(null=True, blank=True)
    alertFlag = models.CharField(max_length=255, null=True, blank=True)
    applicationFailurePath = models.CharField(max_length=255, null=True, blank=True)
    applicationReturnPath = models.CharField(max_length=255, null=True, blank=True)
    authCode = models.CharField(max_length=255, null=True, blank=True)
    bankShare = models.FloatField(null=True, blank=True)
    bankTxnId = models.CharField(max_length=255, null=True, blank=True)
    challanNo = models.CharField(max_length=255, null=True, blank=True)
    clientId = models.IntegerField(null=True, blank=True)
    clientName = models.CharField(max_length=255, null=True, blank=True)
    clientRequestIP = models.CharField(max_length=255, null=True, blank=True)
    clientTxnId = models.CharField(max_length=255, null=True, blank=True)
    convifee = models.FloatField(null=True, blank=True)
    enquiryCounter = models.IntegerField(null=True, blank=True)
    enquiryDate = models.DateTimeField(null=True, blank=True)
    ePcharges = models.FloatField(null=True, blank=True)
    IntHandCharges = models.FloatField(null=True, blank=True)
    mappingId = models.IntegerField(null=True, blank=True)
    paidAmount = models.FloatField(null=True, blank=True)
    payeeAmount = models.FloatField(null=True, blank=True)
    payeeEmail = models.CharField(max_length=255, null=True, blank=True)
    payeeFirstName = models.CharField(max_length=255, null=True, blank=True)
    payeeLstName = models.CharField(max_length=255, null=True, blank=True)
    payeeMidName = models.CharField(max_length=255, null=True, blank=True)
    payeeMob = models.CharField(max_length=255, null=True, blank=True)
    paymentMode = models.CharField(max_length=255, null=True, blank=True)
    PGName = models.CharField(max_length=255, null=True, blank=True)
    PGPayMode = models.CharField(max_length=255, null=True, blank=True)
    PGResponseCode = models.CharField(max_length=255, null=True, blank=True)
    PGReturnAmount = models.FloatField(null=True, blank=True)
    PGTxnId = models.CharField(max_length=255, null=True, blank=True)
    programID = models.CharField(max_length=255, null=True, blank=True)
    qCBId = models.CharField(max_length=255, null=True, blank=True)
    qCCID = models.CharField(max_length=255, null=True, blank=True)
    reSeller1Share = models.FloatField(null=True, blank=True)
    reSeller2Share = models.FloatField(null=True, blank=True)
    reSeller3Share = models.FloatField(null=True, blank=True)
    refundDate = models.CharField(max_length=255, null=True, blank=True)
    regNumber = models.CharField(max_length=255, null=True, blank=True)
    resMsg = models.CharField(max_length=255, null=True, blank=True)
    sabPaisaRespCode = models.CharField(max_length=255, null=True, blank=True)
    serviceCharge = models.FloatField(null=True, blank=True)
    sPshare = models.FloatField(null=True, blank=True)
    studentPayCycle = models.CharField(max_length=255, null=True, blank=True)
    studentUIN = models.CharField(max_length=255, null=True, blank=True)
    transCompleteDate = models.DateTimeField(null=True, blank=True)
    transDate = models.DateTimeField(null=True, blank=True)
    uitApplicationId = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'transaction_detail'
        app_label = 'transactions'
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['client_code']),
            models.Index(fields=['client_txn_id']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_mode']),
            models.Index(fields=['trans_date']),
            models.Index(fields=['settlement_date']),
            models.Index(fields=['is_settled']),
        ]

    def __str__(self):
        return f"{self.txn_id} - {self.client_name}"

    @property
    def payee_name(self):
        """Combine payee names"""
        parts = []
        if self.payee_first_name:
            parts.append(self.payee_first_name)
        if self.payee_mid_name:
            parts.append(self.payee_mid_name)
        if self.payee_lst_name:
            parts.append(self.payee_lst_name)
        return ' '.join(parts) if parts else ''


class ClientRequestTempStore(models.Model):
    """
    Client Request Temp Store model with exact fields from database
    """
    # Composite primary key (handled at database level)
    client_code = models.CharField(max_length=255)
    client_txn_id = models.CharField(max_length=255)

    # Payee address information
    payee_address = models.CharField(max_length=255, default='NA', null=True, blank=True)
    payee_address1 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    payee_address2 = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Application information
    amount_type = models.CharField(max_length=255, default='NA', null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    application_name = models.CharField(max_length=255, null=True, blank=True)

    # Bank and branch
    bid = models.CharField(max_length=255, null=True, blank=True)
    branch = models.CharField(max_length=255, default='NA', null=True, blank=True)
    bank_id = models.IntegerField(null=True, blank=True)

    # Options and settings
    by_pass_option = models.CharField(max_length=255, default='0', null=True, blank=True)

    # Card information
    card_holder_name = models.CharField(max_length=255, default='NA', null=True, blank=True)
    card_number = models.CharField(max_length=50, default='NA', null=True, blank=True)
    card_type = models.CharField(max_length=255, default='NA', null=True, blank=True)
    card_exp_month = models.CharField(max_length=10, null=True, blank=True)
    card_exp_year = models.CharField(max_length=10, null=True, blank=True)

    # Client information
    cid = models.CharField(max_length=255, null=True, blank=True)
    client_check_sum = models.CharField(max_length=255, default='NA', null=True, blank=True)
    client_endpoint = models.CharField(max_length=255, null=True, blank=True)
    client_failed_ru_url = models.CharField(max_length=255, null=True, blank=True)
    client_id = models.CharField(max_length=255, default='NA', null=True, blank=True)
    client_key = models.CharField(max_length=255, null=True, blank=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_paymode = models.CharField(max_length=255, null=True, blank=True)
    client_return_url = models.CharField(max_length=255, null=True, blank=True)
    client_app_id = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Charges
    conv_charges = models.FloatField(null=True, blank=True)
    ep_charges = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)

    # Personal information
    email_id = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=255, null=True, blank=True)

    # Dates
    end_date = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.CharField(max_length=255, null=True, blank=True)
    expiry_date = models.CharField(max_length=255, null=True, blank=True)
    txn_ini_date = models.DateTimeField()
    trans_complete_date = models.DateTimeField(null=True, blank=True)

    # IDs and numbers
    end_point_id = models.CharField(max_length=255, default='NA', null=True, blank=True)
    enrollment_number = models.CharField(max_length=255, default='NA', null=True, blank=True)
    gr_number = models.CharField(max_length=255, default='NA', null=True, blank=True)
    partner_id = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Amounts
    paid_amount = models.FloatField(null=True, blank=True)
    txn_amount = models.FloatField(null=True, blank=True)
    request_amount = models.CharField(max_length=255, null=True, blank=True)
    donation_amount = models.FloatField(default=0, null=True, blank=True)

    # Authentication
    password = models.CharField(max_length=255, default='NA', null=True, blank=True)
    user_name = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Payment information
    pay_cycle = models.CharField(max_length=255, null=True, blank=True)
    payment_mode_id = models.CharField(max_length=255, default='NA', null=True, blank=True)
    payment_brand = models.CharField(max_length=255, default='NA', null=True, blank=True)
    payer_account_number = models.CharField(max_length=50, null=True, blank=True)
    payer_vpa = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Payee information
    payee_contact_number = models.CharField(max_length=255, null=True, blank=True)
    payee_email = models.CharField(max_length=255, null=True, blank=True)
    payee_first_name = models.CharField(max_length=255, null=True, blank=True)
    payee_last_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mid_name = models.CharField(max_length=255, null=True, blank=True)

    # Profile and program
    profile = models.CharField(max_length=255, default='NA', null=True, blank=True)
    program_id = models.CharField(max_length=255, null=True, blank=True)

    # Academic
    semester = models.CharField(max_length=255, default='NA', null=True, blank=True)
    student_pay_cycle = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # UDF fields (User Defined Fields)
    udf1 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf2 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf3 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf4 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf5 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf6 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf7 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf8 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf9 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf10 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf11 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf12 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf13 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf14 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf15 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf16 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf17 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf18 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf19 = models.CharField(max_length=255, default='NA', null=True, blank=True)
    udf20 = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # Channel
    channel_id = models.CharField(max_length=255, null=True, blank=True)
    challan_no = models.CharField(max_length=100, default='NA', null=True, blank=True)

    # Page and transfer
    page_load = models.IntegerField(default=0, null=True, blank=True)
    mode_transfer = models.CharField(max_length=255, default='NA', null=True, blank=True)

    # MCC
    mcc = models.CharField(max_length=20, null=True, blank=True)

    # Response and status
    sabpaisa_resp_code = models.CharField(max_length=50, null=True, blank=True)
    sabpaisa_errorcode = models.CharField(max_length=100, default='NA', null=True, blank=True)
    sabpaisa_message = models.CharField(max_length=100, default='NA', null=True, blank=True)
    status = models.CharField(max_length=50, default='NA', null=True, blank=True)

    # Browser and source
    browser_details = models.CharField(max_length=255, null=True, blank=True)
    merchant_payment_source_url = models.CharField(max_length=255, null=True, blank=True)
    seamless_type = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'client_request_temp_store'
        app_label = 'transactions'
        unique_together = [['client_code', 'client_txn_id']]  # Composite key
        indexes = [
            models.Index(fields=['client_code']),
            models.Index(fields=['client_txn_id']),
            models.Index(fields=['txn_ini_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.client_code} - {self.client_txn_id}"

    @property
    def payee_full_name(self):
        """Combine payee names"""
        parts = []
        if self.payee_first_name:
            parts.append(self.payee_first_name)
        if self.payee_mid_name:
            parts.append(self.payee_mid_name)
        if self.payee_last_name:
            parts.append(self.payee_last_name)
        return ' '.join(parts) if parts else ''

    @property
    def full_name(self):
        """Combine first and last name"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return ' '.join(parts) if parts else ''