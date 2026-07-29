from rest_framework import serializers
from apps.workforce.models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action',
            'model_name', 'object_id', 'description',
            'old_value', 'new_value', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None