from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from apps.workforce.models import Employee, ExitInterview
from apps.workforce.serializers.exit_interview import ExitInterviewSerializer
from apps.workforce.services import send_exit_interview, submit_exit_interview
from datetime import date


class ExitInterviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        interviews = ExitInterview.objects.select_related(
            'employee',
            'employee__professional_details',
            'employee__professional_details__department',
            'employee__professional_details__reporting_to',
            'response',   # no more primary_reason FK
        ).filter(deleted=False)
        return Response(ExitInterviewSerializer(interviews, many=True).data)


class SendExitInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, emp_pk):
        emp       = get_object_or_404(Employee, pk=emp_pk)
        interview = send_exit_interview(employee=emp, sent_by=request.user)
        return Response(ExitInterviewSerializer(interview).data, status=201)


class SubmitExitInterviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, emp_id, token):
        interview = get_object_or_404(
        ExitInterview.objects.select_related(
        'employee',
        'employee__professional_details',
        'employee__professional_details__department',
        'employee__professional_details__reporting_to',
        ),
        employee__id=emp_id,
        token=token,
        )

        already_submitted = interview.status == 'submitted'

        prof = getattr(interview.employee, 'professional_details', None)

        joined_on = prof.joined_on if prof else None
        exit_date = prof.exit_date if prof else None

        length_of_service = ''

        if joined_on and exit_date:
            days = (exit_date - joined_on).days
            years = days // 365
            months = (days % 365) // 30
            length_of_service = f"{years} Years {months} Months"

        hod_name = ''
        if prof and prof.department:
            manager = prof.department.managers.filter(
                is_active=True
            ).select_related('emp').first()

            if manager and manager.emp:
                hod_name = manager.emp.full_name
            return Response({
                'employee_name': interview.employee.full_name,
                'status': interview.status,
                'already_submitted': already_submitted,
                'employee_info': {
                    'full_name': interview.employee.full_name,

                    'department': (
                        prof.department.name
                        if prof and prof.department
                        else ''
                    ),

                    'designation': (
                        prof.designation
                        if prof
                        else ''
                    ),

                    'joined_on': (
                        str(joined_on)
                        if joined_on
                        else ''
                    ),

                    'separation_date': (
                        str(prof.exit_date)
                        if prof and prof.exit_date
                        else ''
                    ),

                    'exit_interview_date': str(date.today()),

                    'length_of_service': length_of_service,

                    'supervisor_name': (
                        prof.reporting_to.full_name
                        if prof and prof.reporting_to
                        else ''
                    ),

                    'head_of_department': (
                        prof.department.manager.full_name
                        if prof and prof.department
                        and hasattr(prof.department, 'manager')
                        and prof.department.manager
                        else ''
                            ),

                    'last_project_worked': (
                        prof.last_project_worked
                        if prof and prof.last_project_worked
                        else ''
                    ),
                }
            })

    def post(self, request, emp_id, token):
        interview = get_object_or_404(
            ExitInterview, employee__id=emp_id, token=token
        )
        if interview.status == 'submitted':
            return Response({'error': 'Already submitted and cannot be edited.'}, status=400)
        try:
            submit_exit_interview(
                interview=interview,
                response_data=request.data,
            )
            return Response({'message': 'Submitted successfully'}, status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)