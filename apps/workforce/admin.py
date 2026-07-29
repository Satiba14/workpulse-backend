from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Department, Employee,
    EmployeeProfessionalDetails, ManagerDetails,
    EmployeeDocumentMaster, ExitReason, AttritionRecord,
    ExitInterview, ExitInterviewResponse,
    Concern, ConcernResponse,
ConcernAccessLog, AuditLog
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['email']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Info', {'fields': ('role', 'emp_id', 'is_active')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(EmployeeProfessionalDetails)
admin.site.register(ManagerDetails)
admin.site.register(EmployeeDocumentMaster)
admin.site.register(ExitReason)
admin.site.register(AttritionRecord)
admin.site.register(ExitInterview)
admin.site.register(ExitInterviewResponse)
admin.site.register(Concern)
admin.site.register(ConcernResponse)
admin.site.register(ConcernAccessLog)
admin.site.register(AuditLog)