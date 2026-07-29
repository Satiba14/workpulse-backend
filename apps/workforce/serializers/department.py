import math
from rest_framework import serializers
from django.db.models import Count, Q
from apps.workforce.models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    parent_department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        allow_null=True,
        required=False
    )
    parent_department_name = serializers.SerializerMethodField()

    # These come from annotated fields added by get_all_departments()
    # so they are NOT computed per-row — they are pre-calculated in the DB
    employee_count     = serializers.IntegerField(read_only=True, default=0)
    billable_count     = serializers.IntegerField(read_only=True, default=0)
    non_billable_count = serializers.IntegerField(read_only=True, default=0)
    buffer_count       = serializers.IntegerField(read_only=True, default=0)
    inactive_count     = serializers.IntegerField(read_only=True, default=0)
    attrition_count    = serializers.IntegerField(read_only=True, default=0)

    # These are computed from annotated values — no extra queries
    attrition_pct = serializers.SerializerMethodField()
    buffer_pct    = serializers.SerializerMethodField()
    hire_needed   = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    manager_id   = serializers.SerializerMethodField()

    def get_manager_name(self, obj):
        mgr = obj.managers.filter(is_active=True).first()
        return mgr.emp.full_name if mgr else None

    def get_manager_id(self, obj):
        mgr = obj.managers.filter(is_active=True).first()
        return str(mgr.emp.id) if mgr else None

    class Meta:
        model = Department
        fields = [
            'id', 'name',
            'parent_department', 'parent_department_name',
            'manager_name',
            'manager_id',
            'is_active',
            'employee_count',
            'billable_count',
            'non_billable_count',
            'buffer_count',
            'inactive_count',
            'attrition_count',
            'attrition_pct',
            'buffer_pct',
            'hire_needed',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_parent_department_name(self, obj):
        return obj.parent_department.name if obj.parent_department else None

    # All three use pre-annotated integers — NO extra DB queries
    def get_attrition_pct(self, obj):
        active  = getattr(obj, 'employee_count', 0) or 0
        exited  = getattr(obj, 'attrition_count', 0) or 0
        total   = active + exited
        return str(round((exited / total) * 100, 1)) if total > 0 else "0.0"

    def get_buffer_pct(self, obj):
        active = getattr(obj, 'employee_count', 0) or 0
        buffer = getattr(obj, 'buffer_count', 0) or 0
        return str(round((buffer / active) * 100, 1)) if active > 0 else "0.0"

    def get_hire_needed(self, obj):
        active   = getattr(obj, 'employee_count', 0) or 0
        buffer   = getattr(obj, 'buffer_count', 0) or 0
        required = math.ceil(active * 0.10)
        return max(0, required - buffer)

class DepartmentCreateSerializer(serializers.ModelSerializer):
    parent_department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Department
        fields = ['name', 'parent_department']