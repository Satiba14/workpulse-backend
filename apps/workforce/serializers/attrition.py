from rest_framework import serializers
from apps.workforce.models import ExitReason, AttritionRecord


class ExitReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExitReason
        fields = [
            'id', 'reason_text', 'keywords',
            'counter', 'is_predefined', 'created_at'
        ]
        read_only_fields = ['id', 'counter', 'created_at']


class AttritionRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source='department.name', read_only=True
    )
    primary_reason_text = serializers.CharField(
        source='primary_reason.reason_text', read_only=True
    )

    class Meta:
        model = AttritionRecord
        fields = [
            'id', 'employee', 'employee_name',
            'exit_date', 'primary_reason', 'primary_reason_text',
            'custom_reason', 'department', 'department_name',
            'recorded_at',
        ]
        read_only_fields = ['id', 'recorded_at', 'recorded_by']

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else None

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['recorded_by'] = request.user
        return super().create(validated_data)