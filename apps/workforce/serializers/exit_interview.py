from rest_framework import serializers
from apps.workforce.models import ExitInterview, ExitInterviewResponse

class ExitInterviewResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ExitInterviewResponse
        exclude = ['exit_interview', 'deleted']
        read_only_fields = ['id', 'submitted_at']

class ExitInterviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id   = serializers.SerializerMethodField()
    employee_info = serializers.SerializerMethodField()
    response      = ExitInterviewResponseSerializer(read_only=True)

    class Meta:
        model  = ExitInterview
        fields = [
            'id', 'employee', 'employee_id', 'employee_name',
            'employee_info', 'token', 'status',
            'sent_at', 'submitted_at', 'response',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'token', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else None

    def get_employee_id(self, obj):
        return str(obj.employee.id) if obj.employee else None

    def get_employee_info(self, obj):
        """Pre-fills the form with known employee data."""
        emp  = obj.employee
        prof = getattr(emp, 'professional_details', None)
        length_of_service = ''
        if prof and prof.joined_on and prof.exit_date:
            days = (prof.exit_date - prof.joined_on).days
            years = days // 365
            months = (days % 365) // 30
            length_of_service = f"{years} Years {months} Months"
        if not emp:
            return {}
        return {
    'full_name': emp.full_name,
    'department': prof.department.name if prof and prof.department else '',
    'designation': prof.designation if prof else '',
    'joined_on': str(prof.joined_on) if prof and prof.joined_on else '',
    'separation_date': str(prof.exit_date) if prof and prof.exit_date else '',
    'length_of_service': length_of_service,
    'exit_interview_date': str(obj.sent_at.date()) if obj.sent_at else '',
    'supervisor_name': prof.reporting_to.full_name if prof and prof.reporting_to else '',
    'head_of_department': (
        prof.department.manager.full_name
        if prof and prof.department and hasattr(prof.department, 'manager')
        and prof.department.manager
        else ''
    ),
    'last_project_worked': '',
}