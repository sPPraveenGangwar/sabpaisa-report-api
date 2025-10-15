"""
Safe transaction models with only confirmed database fields
This is a minimal version that only includes fields confirmed to exist
"""
from django.db import models


class TransactionDetailSafe(models.Model):
    """
    Minimal TransactionDetail model with only core fields
    """
    # Primary identifier
    txn_id = models.CharField(max_length=255, primary_key=True)

    # Core transaction fields from SQL
    act_amount = models.FloatField(null=True, blank=True)
    pg_name = models.CharField(max_length=255, null=True, blank=True)
    pg_pay_mode = models.CharField(max_length=255, null=True, blank=True)
    pg_response_code = models.CharField(max_length=255, null=True, blank=True)
    pg_return_amount = models.FloatField(null=True, blank=True)
    pg_txn_id = models.CharField(max_length=255, null=True, blank=True)

    # Alert and amount fields
    alert_flag = models.CharField(max_length=255, null=True, blank=True)
    amount_type = models.CharField(max_length=255, null=True, blank=True)

    # URLs
    application_fail_url = models.CharField(max_length=255, null=True, blank=True)
    application_succ_url = models.CharField(max_length=255, null=True, blank=True)

    # Bank details
    auth_code = models.CharField(max_length=255, null=True, blank=True)
    bank_txn_id = models.CharField(max_length=255, null=True, blank=True)
    challan_no = models.CharField(max_length=255, null=True, blank=True)

    # Client information
    client_id = models.IntegerField(null=True, blank=True, db_index=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_request_ip = models.CharField(max_length=255, null=True, blank=True)
    client_code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    client_txn_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # Charges
    convcharges = models.FloatField(null=True, blank=True)
    ep_charges = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)

    # Amounts
    paid_amount = models.FloatField(null=True, blank=True)
    payee_amount = models.FloatField(null=True, blank=True)

    # Payee information
    payee_email = models.CharField(max_length=255, null=True, blank=True)
    payee_first_name = models.CharField(max_length=255, null=True, blank=True)
    payee_lst_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mid_name = models.CharField(max_length=255, null=True, blank=True)
    payee_mob = models.CharField(max_length=255, null=True, blank=True)

    # Payment details
    payment_mode = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    program_id = models.CharField(max_length=255, null=True, blank=True)

    # Refund fields
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_message = models.CharField(max_length=255, null=True, blank=True)
    refund_status_code = models.CharField(max_length=255, null=True, blank=True)

    # Other identifiers
    reg_number = models.CharField(max_length=255, null=True, blank=True)
    resp_msg = models.CharField(max_length=255, null=True, blank=True)
    sabpaisa_resp_code = models.CharField(max_length=255, null=True, blank=True)

    # Status and dates
    status = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    trans_complete_date = models.DateTimeField(null=True, blank=True)
    trans_date = models.DateTimeField(db_index=True)

    # Additional fields
    uit_application_id = models.CharField(max_length=255, null=True, blank=True)
    vpa = models.CharField(max_length=255, null=True, blank=True)
    vpa_remarks = models.CharField(max_length=255, null=True, blank=True)

    # Settlement fields
    is_settled = models.BooleanField(null=True, blank=True, db_index=True)
    pag_response_code = models.CharField(max_length=255, null=True, blank=True)
    charge_back_amount = models.FloatField(null=True, blank=True)
    charge_back_date = models.DateTimeField(null=True, blank=True)
    charge_back_status = models.CharField(max_length=255, null=True, blank=True)
    settlement_date = models.DateTimeField(null=True, blank=True, db_index=True)
    settlement_amount = models.FloatField(null=True, blank=True)
    channel_id = models.CharField(max_length=255, null=True, blank=True)

    # Enquiry fields
    enquiry_counter = models.IntegerField(null=True, blank=True, default=0)
    enquiry_date = models.DateTimeField(null=True, blank=True)
    mapping_id = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False  # Don't create migrations
        db_table = 'transaction_detail'
        app_label = 'transactions'

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