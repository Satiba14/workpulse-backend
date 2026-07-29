from rest_framework import serializers
from apps.workforce.models import Concern, ConcernResponse, ConcernAccessLog


class ConcernResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ConcernResponse
        fields = [
            'id', 'response_text', 'audio_file_path',
            'document_file_path', 'is_private', 'responded_at',
        ]
        read_only_fields = ['id', 'responded_at']


class ConcernSerializer(serializers.ModelSerializer):
    employee_name   = serializers.SerializerMethodField()
    employee_emp_id = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    reviewed_by_email = serializers.SerializerMethodField()
    has_response    = serializers.SerializerMethodField()
    response        = ConcernResponseSerializer(read_only=True)

    class Meta:
        model  = Concern
        fields = [
            'id', 'employee', 'employee_name', 'employee_emp_id',
            'created_by', 'created_by_email',
            'reason_category', 'message',
            'status', 'priority',
            'unique_token', 'email_sent_at',
            'reviewed_by', 'reviewed_by_email',
            'has_response', 'response',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'unique_token', 'email_sent_at',
            'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else None

    def get_employee_emp_id(self, obj):
        # Use employee's UUID short form as display ID
        return str(obj.employee.id)[:8].upper() if obj.employee else None

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_reviewed_by_email(self, obj):
        return obj.reviewed_by.email if obj.reviewed_by else None

    def get_has_response(self, obj):
        try:
            return obj.response is not None
        except ConcernResponse.DoesNotExist:
            return False