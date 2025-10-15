"""
QwikForms Serializers
Serializers for QwikForms transaction and form data
"""
from rest_framework import serializers
from .models import DataTransactions, DataForm, DataFormDetails, CollegeMaster, LookupFormPayers, ClientMappingCode, BankDetailsBean
import json


class DataFormDetailsSerializer(serializers.ModelSerializer):
    """Form Configuration Details"""
    class Meta:
        model = DataFormDetails
        fields = [
            'id', 'form_date', 'form_name', 'form_owner_id', 'form_owner_name',
            'form_start_date', 'form_end_date', 'form_late_end_date',
            'status', 'payer_type', 'move_to_pg', 'form_response_url',
            'is_display_service_charge', 'is_aadhaar_verified', 'is_pan_verified'
        ]


class DataFormSerializer(serializers.ModelSerializer):
    """Form Submission Data"""
    form_data_json = serializers.SerializerMethodField()

    class Meta:
        model = DataForm
        fields = [
            'form_id', 'form_applicant_id', 'form_data', 'form_data_json', 'form_date',
            'form_fee_id', 'form_inst_id', 'form_template_id', 'form_trans_id',
            'form_client_id', 'form_fee_name', 'contact', 'dob_date', 'email',
            'form_end_date', 'form_start_date', 'name', 'trans_amount',
            'udf_field1', 'udf_field2', 'udf_field3', 'udf_field4', 'udf_field5',
            'udf_field6', 'udf_field7', 'udf_field8', 'udf_field9', 'udf_field10',
            'code', 'form_status', 'form_number', 'payer_id', 'payer_aadhaar', 'payer_pan'
        ]

    def get_form_data_json(self, obj):
        """Parse form_data JSON if exists"""
        if obj.form_data:
            try:
                return json.loads(obj.form_data)
            except (json.JSONDecodeError, TypeError):
                return None
        return None


class CollegeMasterSerializer(serializers.ModelSerializer):
    """Client/Institute Information"""
    class Meta:
        model = CollegeMaster
        fields = [
            'college_id', 'college_code', 'college_name', 'state',
            'address', 'contact', 'email_id', 'college_url'
        ]


class DataTransactionsSerializer(serializers.ModelSerializer):
    """QwikForms Transaction Data - Basic"""
    client_name = serializers.SerializerMethodField()
    form_name = serializers.SerializerMethodField()

    class Meta:
        model = DataTransactions
        fields = [
            'id', 'trans_id', 'sp_trans_id', 'trans_date', 'trans_amount',
            'trans_status', 'trans_paymode', 'name', 'email', 'contact',
            'fee_name', 'client_id', 'bid', 'cid', 'client_name', 'form_name',
            'form_id', 'trans_charges', 'act_amount', 'pg_trans_id', 'bank_reference_no',
            'settlement_status', 'settlement_date', 'settlement_amount', 'is_settled'
        ]

    def get_client_name(self, obj):
        """Get client name from college_id_fk"""
        if obj.college_id_fk:
            try:
                # If college_id_fk is already a CollegeMaster object (ForeignKey), use it directly
                if isinstance(obj.college_id_fk, CollegeMaster):
                    return obj.college_id_fk.college_name
                # Otherwise, it's an ID, fetch the object
                else:
                    college = CollegeMaster.objects.using('qwikforms_db').get(college_id=obj.college_id_fk)
                    return college.college_name
            except (CollegeMaster.DoesNotExist, AttributeError, ValueError):
                return None
        return None

    def get_form_name(self, obj):
        """Get form name from form_id"""
        if obj.form_id:
            try:
                form = DataForm.objects.using('qwikforms_db').get(form_id=obj.form_id)
                return form.form_fee_name
            except DataForm.DoesNotExist:
                return None
        return None


class DataTransactionsDetailedSerializer(serializers.ModelSerializer):
    """QwikForms Transaction Data - Detailed with Form Data"""
    form_details = serializers.SerializerMethodField()
    client_details = serializers.SerializerMethodField()

    class Meta:
        model = DataTransactions
        fields = '__all__'

    def get_form_details(self, obj):
        """Get related form submission data"""
        if obj.form_id:
            try:
                form = DataForm.objects.using('qwikforms_db').get(form_id=obj.form_id)
                return DataFormSerializer(form).data
            except DataForm.DoesNotExist:
                return None
        return None

    def get_client_details(self, obj):
        """Get client/institute details"""
        if obj.college_id_fk:
            try:
                college = CollegeMaster.objects.using('qwikforms_db').get(college_id=obj.college_id_fk)
                return CollegeMasterSerializer(college).data
            except CollegeMaster.DoesNotExist:
                return None
        return None


class QwikFormsTransactionWithFormSerializer(serializers.Serializer):
    """Combined Transaction and Form Data"""
    # Transaction fields
    transaction_id = serializers.IntegerField(source='id')
    trans_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sp_trans_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    trans_date = serializers.DateTimeField(required=False, allow_null=True)
    trans_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    trans_status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    trans_paymode = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Payment Gateway fields
    pg_trans_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    pg_resp_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    bank_reference_no = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Customer fields
    customer_name = serializers.CharField(source='name', required=False, allow_null=True, allow_blank=True)
    customer_email = serializers.CharField(source='email', required=False, allow_null=True, allow_blank=True)
    customer_contact = serializers.CharField(source='contact', required=False, allow_null=True, allow_blank=True)

    # Financial fields
    act_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    trans_charges = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    trans_other_chrg = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # Settlement fields
    settlement_status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    settlement_date = serializers.DateField(required=False, allow_null=True)
    settlement_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    is_settled = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Refund fields
    refund_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    refund_amount = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    refund_submit_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    refund_close_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Form related fields
    form_id = serializers.IntegerField(required=False, allow_null=True)
    form_fee_name = serializers.CharField(source='fee_name', required=False, allow_null=True, allow_blank=True)

    # Client fields
    client_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    client_code = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    bid = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cid = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Form data (nested)
    form_data = serializers.SerializerMethodField()

    def get_client_code(self, obj):
        """Get client code from bid/cid mapping"""
        if hasattr(obj, 'bid') and obj.bid and hasattr(obj, 'cid') and obj.cid:
            try:
                mapping = ClientMappingCode.objects.using('qwikforms_db').filter(
                    bid=obj.bid,
                    cid=obj.cid
                ).first()
                if mapping:
                    return mapping.cm_code
            except Exception:
                pass
        return None

    def get_client_name(self, obj):
        """Get client name from bid/cid mapping or college_id_fk"""
        # First try bid/cid mapping
        if hasattr(obj, 'bid') and obj.bid and hasattr(obj, 'cid') and obj.cid:
            try:
                mapping = ClientMappingCode.objects.using('qwikforms_db').filter(
                    bid=obj.bid,
                    cid=obj.cid
                ).first()
                if mapping and mapping.college_bean_mapping_to_sab_paisa_client_college_id:
                    college = CollegeMaster.objects.using('qwikforms_db').get(
                        college_id=mapping.college_bean_mapping_to_sab_paisa_client_college_id
                    )
                    return college.college_name
            except Exception:
                pass

        # Fallback to college_id_fk - check if it's already a ForeignKey object or an ID
        if hasattr(obj, 'college_id_fk') and obj.college_id_fk:
            try:
                # If college_id_fk is already a CollegeMaster object (ForeignKey), use it directly
                if isinstance(obj.college_id_fk, CollegeMaster):
                    return obj.college_id_fk.college_name
                # Otherwise, it's an ID, fetch the object
                else:
                    college = CollegeMaster.objects.using('qwikforms_db').get(college_id=obj.college_id_fk)
                    return college.college_name
            except (CollegeMaster.DoesNotExist, AttributeError, ValueError):
                pass

        return None

    def get_bank_name(self, obj):
        """Get bank name from bid"""
        if hasattr(obj, 'bid') and obj.bid:
            try:
                # bid might be bank_id or need mapping
                # Try direct bank_id first
                bank = BankDetailsBean.objects.using('qwikforms_db').filter(
                    bank_id=obj.bid
                ).first()
                if bank:
                    return bank.bankname

                # Try string match
                bank = BankDetailsBean.objects.using('qwikforms_db').filter(
                    bankname__icontains=obj.bid
                ).first()
                if bank:
                    return bank.bankname
            except Exception:
                pass
        return None

    def get_form_data(self, obj):
        """Get form submission data"""
        if hasattr(obj, 'form_id') and obj.form_id:
            try:
                form = DataForm.objects.using('qwikforms_db').get(form_id=obj.form_id)
                form_serializer = DataFormSerializer(form)
                return form_serializer.data
            except DataForm.DoesNotExist:
                return None
        return None


class QwikFormsSettlementSerializer(serializers.Serializer):
    """Settlement Report Serializer"""
    transaction_id = serializers.IntegerField()
    trans_id = serializers.CharField()
    sp_trans_id = serializers.CharField()
    trans_date = serializers.DateTimeField()
    trans_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    settlement_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    settlement_date = serializers.DateField()
    settlement_status = serializers.CharField()
    settlement_by = serializers.CharField()
    is_settled = serializers.CharField()
    trans_charges = serializers.DecimalField(max_digits=15, decimal_places=2)
    customer_name = serializers.CharField()
    customer_email = serializers.CharField()
    customer_contact = serializers.CharField()
    form_fee_name = serializers.CharField()
    client_name = serializers.SerializerMethodField()

    def get_client_name(self, obj):
        """Get client name"""
        if hasattr(obj, 'college_id_fk') and obj.college_id_fk:
            try:
                # If college_id_fk is already a CollegeMaster object (ForeignKey), use it directly
                if isinstance(obj.college_id_fk, CollegeMaster):
                    return obj.college_id_fk.college_name
                # Otherwise, it's an ID, fetch the object
                else:
                    college = CollegeMaster.objects.using('qwikforms_db').get(college_id=obj.college_id_fk)
                    return college.college_name
            except (CollegeMaster.DoesNotExist, AttributeError, ValueError):
                return None
        return None


class QwikFormsRefundSerializer(serializers.Serializer):
    """Refund Report Serializer"""
    transaction_id = serializers.IntegerField()
    trans_id = serializers.CharField()
    sp_trans_id = serializers.CharField()
    trans_date = serializers.DateTimeField()
    trans_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    refund_id = serializers.CharField()
    refund_amount = serializers.CharField()
    refund_submit_date = serializers.CharField()
    refund_close_date = serializers.CharField()
    refund_job = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.CharField()
    customer_contact = serializers.CharField()
    form_fee_name = serializers.CharField()
    trans_status = serializers.CharField()


class QwikFormsAnalyticsSerializer(serializers.Serializer):
    """Analytics Summary Serializer"""
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    total_volume = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_settled_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    pending_settlement_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_refund_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    avg_transaction_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    by_payment_mode = serializers.DictField()
    by_form = serializers.ListField()
    by_client = serializers.ListField()
    daily_trend = serializers.ListField()