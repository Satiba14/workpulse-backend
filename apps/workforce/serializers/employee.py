from rest_framework import serializers
import re
from apps.workforce.models import (
    Employee, EmployeeProfessionalDetails,
    EmployeeDocumentMaster, ManagerDetails
)

class EmployeeProfessionalSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    reporting_to_name = serializers.CharField(source='reporting_to.full_name',read_only=True)

    class Meta:
        model = EmployeeProfessionalDetails
        fields = [
            'id', 'department', 'department_name', 'designation',
            'reporting_to', 'reporting_to_name','joined_on', 'is_active',
            'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocumentMaster
        fields = [
            'id', 'name', 'unique_id',
            'file_path', 'private_key', 'public_key',
            'deleted', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    department_id   = serializers.SerializerMethodField()
    reporting_to_name = serializers.SerializerMethodField()
    is_active       = serializers.SerializerMethodField()
    status          = serializers.SerializerMethodField()
    joined_on       = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'phone_no','email',
            'department_name', 'department_id', 'reporting_to_name',
            'status', 'is_active', 'joined_on', 'created_at',
        ]

    def get_status(self, obj):
        prof = getattr(obj, 'professional_details', None)
        return prof.status if prof else 'inactive'

    def get_department_name(self, obj):
        prof = getattr(obj, 'professional_details', None)
        return prof.department.name if prof and prof.department else None

    def get_department_id(self, obj):
        prof = getattr(obj, 'professional_details', None)
        return str(prof.department_id) if prof and prof.department_id else None
    
    def get_reporting_to_name(self, obj):
        try:
            prof = obj.professional_details

            if prof.reporting_to:
                return prof.reporting_to.full_name

            return None

        except Exception:
            return None

    def get_is_active(self, obj):
        prof = getattr(obj, 'professional_details', None)
        return prof.is_active if prof else False

    def get_joined_on(self, obj):
        prof = getattr(obj, 'professional_details', None)
        return str(prof.joined_on) if prof and prof.joined_on else None


class EmployeeDetailSerializer(serializers.ModelSerializer):
    professional_details = EmployeeProfessionalSerializer(read_only=True)
    documents            = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            # Core
            'id',
            # Personal
            'first_name', 'last_name',
            'phone_no','email', 'alternative_phone_no',
            'date_of_birth', 'gender', 'blood_group', 'marital_status',
            # Address — split into current / permanent / aadhaar
            'current_address', 'current_pincode', 'current_city', 'current_state',
            'permanent_address', 'permanent_pincode', 'permanent_city', 'permanent_state',
            'aadhaar_address', 'nation',
            # Legacy fields (kept for backward compat)
            'address', 'pincode', 'state', 'district',
            # Family
            'father_name', 'mother_name', 'spouse_name',
            # Nested
            'professional_details', 'documents',
            # Timestamps
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_documents(self, obj):
        prof = getattr(obj, 'professional_details', None)
        if prof:
            docs = prof.documents.filter(deleted=False)
            return EmployeeDocumentSerializer(docs, many=True).data
        return []


class EmployeeCreateSerializer(serializers.Serializer):
    # Personal
    first_name            = serializers.CharField(max_length=100)
    last_name             = serializers.CharField(max_length=100)
    phone_no              = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=True)
    alternative_phone_no  = serializers.CharField(max_length=15, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(
    choices=['male','female','other'],
    required=True)
    blood_group = serializers.ChoiceField(
    choices=['A+','A-','B+','B-','O+','O-','AB+','AB-'],
    required=True)
    marital_status = serializers.ChoiceField(
    choices=['single','married','divorced','widowed'],
    required=True)
    # Address
    current_address = serializers.CharField(required=True)
    current_pincode = serializers.CharField(max_length=10, required=True)
    current_city = serializers.CharField(max_length=100, required=True)
    current_state = serializers.CharField(max_length=100, required=True)

    permanent_address = serializers.CharField(required=True)
    permanent_pincode = serializers.CharField(max_length=10, required=True)
    permanent_city = serializers.CharField(max_length=100, required=True)
    permanent_state = serializers.CharField(max_length=100, required=True)
    aadhaar_address       = serializers.CharField(required=False, allow_blank=True)
    nation                = serializers.CharField(max_length=100, required=False, allow_blank=True)
    # Family
    father_name = serializers.CharField(max_length=150, required=True)
    mother_name = serializers.CharField(max_length=150, required=True)
    spouse_name           = serializers.CharField(max_length=150, required=False, allow_blank=True)
    # Professional
    department = serializers.UUIDField(required=True)
    designation = serializers.CharField(max_length=100,required=True)
    joined_on = serializers.DateField(required=True)
    reporting_to          = serializers.UUIDField(required=False, allow_null=True)
    status                = serializers.ChoiceField(
        choices=['billable', 'non_billable', 'buffer', 'inactive'],
        default='billable'
    )

    def validate_phone_no(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits."
            )
        return value

    def validate_current_pincode(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError(
                "Current pincode must be 6 digits."
            )
        return value

    def validate_permanent_pincode(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError(
                "Permanent pincode must be 6 digits."
            )
        return value

    def validate_email(self, value):
        value = value.strip().lower()

        pattern = r'^[a-zA-Z0-9._%+-]+@invenger\.com$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Enter a valid Invenger company email address."
            )

        return value
    


class ManagerDetailsSerializer(serializers.ModelSerializer):
    employee_name   = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ManagerDetails
        fields = ['id', 'department', 'department_name', 'emp', 'employee_name',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return obj.emp.full_name if obj.emp else None