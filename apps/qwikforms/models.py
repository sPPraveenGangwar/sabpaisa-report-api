"""
QwikForms Models - Connects to spQwikForm database
Admin-only access for QwikForms transaction and form data
"""
from django.db import models


class BankDetailsBean(models.Model):
    """Bank Details Master"""
    bank_id = models.AutoField(db_column='bankId', primary_key=True)
    bankname = models.CharField(max_length=255, null=True)
    branch = models.CharField(max_length=255, null=True)
    contact_number = models.BigIntegerField(db_column='contactNumber', null=True)
    contact_person = models.CharField(db_column='contactPerson', max_length=255, null=True)
    email_id = models.CharField(db_column='emailId', max_length=255, null=True)
    bank_logo = models.CharField(db_column='bankLogo', max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    bank_image = models.BinaryField(db_column='bankImage', null=True)
    bank_link = models.CharField(db_column='bankLink', max_length=255, null=True)
    comp_id_fk = models.IntegerField(db_column='comp_id_fk', null=True)

    class Meta:
        managed = False
        db_table = 'bank_details_bean'
        app_label = 'qwikforms'


class CollegeMaster(models.Model):
    """Client/Institute Master"""
    college_id = models.AutoField(db_column='collegeId', primary_key=True)
    college_code = models.CharField(db_column='collegeCode', max_length=255, null=True)
    college_name = models.CharField(db_column='collegeName', max_length=255, null=True)
    login_bean_login_id = models.IntegerField(db_column='loginBean_loginId', null=True)
    state = models.CharField(max_length=255, null=True)
    bank_details_otm_bank_id = models.IntegerField(db_column='bankDetailsOTM_bankId', null=True)
    head_organiztion_details_organiztion_id = models.IntegerField(db_column='headOrganiztionDetails_organiztionId', null=True)
    college_logo = models.CharField(db_column='collegeLogo', max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    contact = models.CharField(max_length=255, null=True)
    email_id = models.CharField(db_column='emailId', max_length=255, null=True)
    egf_days = models.IntegerField(db_column='eGFDays', null=True)
    college_image = models.BinaryField(db_column='CollegeImage', null=True)
    college_file = models.BinaryField(db_column='collegeFile', null=True)
    state_id_fk = models.IntegerField(db_column='stateId_Fk', null=True)
    service_id_fk = models.IntegerField(db_column='serviceId_Fk', null=True)
    col_id_fk = models.IntegerField(db_column='colId_Fk', null=True)
    comp_id_fk = models.IntegerField(db_column='comp_id_fk', null=True)
    college_url = models.CharField(db_column='collegeURL', max_length=255, null=True)
    client_image_path = models.CharField(db_column='clientImagePath', max_length=255, null=True)
    id_for_cob = models.CharField(db_column='idForCob', max_length=255, null=True)
    is_refund_enabled = models.CharField(db_column='isRefundEnabled', max_length=45, null=True)
    auth_iv = models.CharField(db_column='authIV', max_length=45, null=True)
    auth_key = models.CharField(db_column='authKey', max_length=45, null=True)
    user_name = models.CharField(db_column='userName', max_length=255, null=True)
    user_password = models.CharField(db_column='userPassword', max_length=255, null=True)

    class Meta:
        managed = False
        db_table = 'college_master'
        app_label = 'qwikforms'


class DataFormDetails(models.Model):
    """Form Configuration Master"""
    id = models.AutoField(primary_key=True)
    form_date = models.DateTimeField(db_column='formDate', null=True)
    form_name = models.CharField(db_column='formName', max_length=255, null=True)
    form_owner_id = models.IntegerField(db_column='formOwnerId', null=True)
    form_fee_id = models.IntegerField(db_column='formFee_id', null=True)
    form_structure_id = models.IntegerField(db_column='formStructure_id', null=True)
    form_end_date = models.DateTimeField(db_column='formEndDate', null=True)
    form_start_date = models.DateTimeField(db_column='formStartDate', null=True)
    payer_type = models.IntegerField(db_column='payer_type', null=True)
    status = models.CharField(max_length=255, null=True)
    status_by = models.IntegerField(db_column='status_by', null=True)
    form_late_end_date = models.DateTimeField(db_column='formLateEndDate', null=True)
    form_owner_name = models.CharField(db_column='formOwnerName', max_length=255, null=True)
    sa_comment = models.CharField(db_column='saComment', max_length=255, null=True)
    validity_flag = models.IntegerField(db_column='validityflag', null=True)
    js_enabled = models.CharField(db_column='jsEnabled', max_length=255, null=True)
    js_name = models.CharField(db_column='js_name', max_length=255, null=True)
    target_actor = models.IntegerField(db_column='target_actor', null=True)
    landingpage_src_path = models.CharField(db_column='landingpage_srcPath', max_length=255, null=True)
    life_cycle = models.CharField(db_column='life_cycle', max_length=255, null=True)
    file_label = models.CharField(db_column='fileLabel', max_length=255, null=True)
    file_ext = models.CharField(db_column='file_ext', max_length=255, null=True)
    has_instructions = models.CharField(db_column='hasInstructions', max_length=255, null=True)
    instructions = models.BinaryField(null=True)
    file_actu_name = models.CharField(db_column='file_actu_name', max_length=255, null=True)
    image = models.CharField(max_length=255, null=True)
    comp_id_fk = models.IntegerField(db_column='comp_id_fk', null=True)
    is_aadhaar_verified = models.CharField(db_column='isAadhaarVerified', max_length=255, null=True)
    is_pan_verified = models.CharField(db_column='isPANVerified', max_length=255, null=True)
    verification_flag = models.CharField(db_column='verificationFlag', max_length=255, null=True)
    validate_field_of_excel = models.CharField(db_column='validateFieldOfExcel', max_length=255, null=True)
    move_to_pg = models.CharField(db_column='moveToPg', max_length=45)
    form_response_url = models.CharField(db_column='formResponseUrl', max_length=255)
    is_display_service_charge = models.CharField(db_column='isDisplayServiceCharge', max_length=20, default='0')

    class Meta:
        managed = False
        db_table = 'data_form_details'
        app_label = 'qwikforms'


class DataForm(models.Model):
    """Form Submission Data"""
    form_id = models.AutoField(db_column='formId', primary_key=True)
    form_applicant_id = models.IntegerField(db_column='formApplicantId', null=True)
    form_data = models.TextField(db_column='formData', null=True)  # JSON stored as longtext
    form_date = models.DateTimeField(db_column='formDate', auto_now_add=True)
    form_fee_id = models.IntegerField(db_column='formFeeId', null=True)
    form_inst_id = models.IntegerField(db_column='formInstId', null=True)
    form_template_id = models.IntegerField(db_column='formTemplateId', null=True)
    form_trans_id = models.CharField(db_column='formTransId', max_length=255, null=True)
    trans_bean_id = models.IntegerField(db_column='transBean_id', null=True)
    form_client_id = models.CharField(db_column='formClientId', max_length=255, null=True)
    form_fee_name = models.CharField(db_column='formFeeName', max_length=255, null=True)
    contact = models.CharField(max_length=255, null=True)
    dob_date = models.DateTimeField(db_column='dobDate', null=True)
    email = models.CharField(max_length=255, null=True)
    form_end_date = models.CharField(db_column='formEndDate', max_length=255, null=True)
    form_start_date = models.CharField(db_column='formStartDate', max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    trans_amount = models.DecimalField(db_column='transAmount', max_digits=15, decimal_places=2, null=True)

    # UDF Fields
    udf_field1 = models.CharField(db_column='udf_field1', max_length=100, default='NA')
    udf_field2 = models.CharField(db_column='udf_field2', max_length=100, default='NA')
    udf_field3 = models.CharField(db_column='udf_field3', max_length=100, default='NA')
    udf_field4 = models.CharField(db_column='udf_field4', max_length=100, default='NA')
    udf_field5 = models.CharField(db_column='udf_field5', max_length=100, default='NA')
    udf_field6 = models.CharField(db_column='udf_field6', max_length=100, default='NA')
    udf_field7 = models.CharField(db_column='udf_field7', max_length=100, default='NA')
    udf_field8 = models.CharField(db_column='udf_field8', max_length=100, default='NA')
    udf_field9 = models.CharField(db_column='udf_field9', max_length=100, default='NA')
    udf_field10 = models.CharField(db_column='udf_field10', max_length=100, default='NA')

    code = models.CharField(max_length=255, null=True)
    form_status = models.CharField(db_column='form_status', max_length=255, null=True)
    formstate_state_id = models.IntegerField(db_column='formstate_state_id', null=True)
    form_number = models.CharField(db_column='formNumber', max_length=255, null=True)
    photo_ext = models.CharField(db_column='photo_ext', max_length=255, null=True)
    photograph = models.BinaryField(null=True)
    signature = models.BinaryField(null=True)
    signature_ext = models.CharField(db_column='signature_ext', max_length=255, null=True)
    payer_id = models.CharField(db_column='payerID', max_length=255, null=True)
    payer_aadhaar = models.CharField(db_column='payerAadhaar', max_length=255, null=True)
    payer_pan = models.CharField(db_column='payerPAN', max_length=255, null=True)

    # File paths
    file_path = models.CharField(db_column='file_Path', max_length=255, null=True)
    file_path1 = models.CharField(db_column='file_Path1', max_length=255, null=True)
    file_path2 = models.CharField(db_column='file_Path2', max_length=255, null=True)
    file_path3 = models.CharField(db_column='file_Path3', max_length=255, null=True)
    file_path4 = models.CharField(db_column='file_Path4', max_length=255, null=True)
    file_path5 = models.CharField(db_column='file_Path5', max_length=255, null=True)
    file_path6 = models.CharField(db_column='file_Path6', max_length=255, null=True)
    file_path7 = models.CharField(db_column='file_Path7', max_length=255, null=True)
    file_path8 = models.CharField(db_column='file_Path8', max_length=255, null=True)
    file_path9 = models.CharField(db_column='file_Path9', max_length=255, null=True)
    file_path10 = models.CharField(db_column='file_Path10', max_length=255, null=True)

    class Meta:
        managed = False
        db_table = 'data_form'
        app_label = 'qwikforms'


class DataTransactions(models.Model):
    """QwikForms Transaction Data"""
    id = models.AutoField(primary_key=True)
    trans_amount = models.DecimalField(db_column='transAmount', max_digits=15, decimal_places=2, null=True)
    trans_date = models.DateTimeField(db_column='transDate', auto_now_add=True)
    trans_id = models.CharField(db_column='transId', max_length=255, null=True)
    trans_id_ext = models.CharField(db_column='transIdExt', max_length=255, null=True)
    trans_paymode = models.CharField(db_column='transPaymode', max_length=255, null=True)
    trans_status = models.CharField(db_column='transStatus', max_length=255, null=True)
    trans_form_form_id = models.IntegerField(db_column='transForm_formId', null=True)
    bank_reference_no = models.CharField(db_column='bankReferenceNo', max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    reference_no = models.CharField(db_column='referenceNo', max_length=255, null=True)
    trans_charges = models.DecimalField(db_column='transCharges', max_digits=15, decimal_places=2, null=True)
    college_id_fk = models.ForeignKey(
        CollegeMaster,
        db_column='college_Id_fk',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='transactions'
    )
    enrollment_number = models.CharField(db_column='enrollmentNumber', max_length=255, null=True)
    fee_names = models.CharField(db_column='feeNames', max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    client_id = models.CharField(db_column='clientId', max_length=255, null=True)
    birth_date = models.DateTimeField(db_column='birthDate', null=True)
    contact_no = models.CharField(db_column='contactNo', max_length=255, null=True)
    payee_profile = models.CharField(db_column='payeeProfile', max_length=255, null=True)
    bid = models.CharField(max_length=255, null=True)
    cid = models.CharField(max_length=255, null=True)
    contact = models.CharField(max_length=255, null=True)
    dob = models.DateTimeField(null=True)
    email = models.CharField(max_length=255, null=True)

    # UDF Fields
    udf_field1 = models.CharField(db_column='udf_field1', max_length=100, default='NA')
    udf_field2 = models.CharField(db_column='udf_field2', max_length=100, default='NA')
    udf_field3 = models.CharField(db_column='udf_field3', max_length=100, default='NA')
    udf_field4 = models.CharField(db_column='udf_field4', max_length=100, default='NA')
    udf_field5 = models.CharField(db_column='udf_field5', max_length=100, default='NA')
    udf_field6 = models.CharField(db_column='udf_field6', max_length=100, default='NA')
    udf_field7 = models.CharField(db_column='udf_field7', max_length=100, default='NA')
    udf_field8 = models.CharField(db_column='udf_field8', max_length=100, default='NA')
    udf_field9 = models.CharField(db_column='udf_field9', max_length=100, default='NA')
    udf_field10 = models.CharField(db_column='udf_field10', max_length=100, default='NA')

    fee_name = models.CharField(db_column='feeName', max_length=255, null=True)
    issuer_ref_no = models.CharField(db_column='issuerRefNo', max_length=255, null=True)
    payer_id = models.CharField(db_column='payerID', max_length=255, null=True)
    pg_resp_code = models.CharField(db_column='pgRespCode', max_length=255, null=True)
    pg_trans_id = models.CharField(db_column='pgTransId', max_length=255, null=True)
    sp_resp_code = models.CharField(db_column='spRespCode', max_length=255, null=True)
    sp_trans_id = models.CharField(db_column='spTransId', max_length=255, null=True)
    trans_og_amount = models.DecimalField(db_column='transOgAmount', max_digits=15, decimal_places=2, null=True)
    trans_other_chrg = models.DecimalField(db_column='transOtherChrg', max_digits=15, decimal_places=2, null=True)
    act_amount = models.DecimalField(db_column='actAmount', max_digits=15, decimal_places=2, null=True)
    refund_job = models.CharField(db_column='refundJob', max_length=255, null=True)
    challan_no = models.CharField(db_column='challanNo', max_length=255, null=True)
    txn_close_date = models.DateTimeField(db_column='txncloseDate', null=True)
    refund_id = models.CharField(db_column='refundId', max_length=50, null=True)
    refund_amount = models.CharField(db_column='refundAmount', max_length=50, null=True)
    refund_submit_date = models.CharField(db_column='refundSubmitDate', max_length=50, null=True)
    refund_close_date = models.CharField(db_column='refundCloseDate', max_length=50, null=True)
    form_id = models.IntegerField(db_column='formId', null=True)

    # Settlement fields
    settlement_amount = models.DecimalField(db_column='settlementAmount', max_digits=15, decimal_places=2, null=True)
    settlement_date = models.DateField(db_column='settlementDate', null=True)
    settlement_by = models.CharField(db_column='settlementBy', max_length=40, null=True)
    settlement_status = models.CharField(db_column='settlementStatus', max_length=50, null=True)
    is_settled = models.CharField(db_column='isSettled', max_length=20, default='false')

    class Meta:
        managed = False
        db_table = 'data_transactions'
        app_label = 'qwikforms'
        indexes = [
            models.Index(fields=['sp_trans_id'], name='indx_spTransId'),
            models.Index(fields=['trans_id'], name='indx_transId'),
        ]

    def __str__(self):
        return f"QF Trans: {self.trans_id} - {self.trans_status}"


class LookupFormPayers(models.Model):
    """Payer Configuration Lookup"""
    payer_id = models.AutoField(primary_key=True)
    payer_type = models.CharField(db_column='payer_type', max_length=255, null=True)
    bid = models.CharField(max_length=255, null=True)
    cid = models.CharField(max_length=255, null=True)
    client_name = models.CharField(db_column='clientName', max_length=255, null=True)

    class Meta:
        managed = False
        db_table = 'lookup_form_payers'
        app_label = 'qwikforms'


class ClientMappingCode(models.Model):
    """Client Mapping Configuration"""
    cmc_id = models.AutoField(db_column='cMCId', primary_key=True)
    bid = models.CharField(max_length=255, null=True)
    cm_code = models.CharField(db_column='cMCode', max_length=255, null=True)
    cm_profile = models.CharField(db_column='cMProfile', max_length=255, null=True)
    cid = models.CharField(max_length=255, null=True)
    college_bean_mapping_to_sabpaisa_client_college_id = models.IntegerField(
        db_column='collegeBeanMappingToSabPaisaClient_collegeId', null=True
    )
    client_url = models.CharField(db_column='clientUrl', max_length=255, null=True)

    class Meta:
        managed = False
        db_table = 'client_mapping_code'
        app_label = 'qwikforms'