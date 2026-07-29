from django.utils import timezone
from apps.workforce.models import ExitInterview, ExitInterviewResponse, ExitReason
from apps.workforce.services.audit import create_audit_log
import requests as http_requests
from django.conf import settings
import logging
from apps.workforce.services.notification import create_notification

logger = logging.getLogger(__name__)

def send_exit_interview(employee, sent_by):
    interview, _ = ExitInterview.objects.get_or_create(employee=employee)
    interview.status  = 'sent'
    interview.sent_at = timezone.now()
    interview.sent_by = sent_by
    interview.save()
    try:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        form_url = f"{frontend_url}/exit-interview/{employee.id}/{interview.token}"

        http_requests.post(
        f"{getattr(settings, 'EMAIL_WEBHOOK_URL', 'http://localhost:3001')}/send-exit-interview",
        json={
            'employee_name':  employee.full_name,
            'employee_email': employee.email,
            'form_link':      form_url,
        },
        timeout=5,)
        
    except Exception as e:
        logger.warning(f"Email webhook failed: {e}")

    try:
        create_notification(
            notif_type='exit_submitted',
            title='Exit Interview Sent',
            message=f'Exit interview sent to {employee.full_name}',
            link='/exit-interviews',
        )
    except Exception as e:
        logger.warning(f"Notification failed: {e}")

    create_audit_log(
        user=sent_by,
        action='update',
        model_name='ExitInterview',
        object_id=interview.id,
        description=f'Exit interview sent to {employee.full_name}',
    )

    return interview


# Fields that exist on ExitInterviewResponse model
RESPONSE_FIELDS = {
    # Section 2
    'joined_for_benefits', 'joined_for_career', 'joined_for_salary',
    'joined_for_reputation', 'joined_for_other',
    # Section 3
    'rating_company_benefits', 'rating_salary', 'rating_working_conditions',
    'rating_advancement', 'rating_others', 'rating_overall',
    # Section 4
    'comm_throughout_company', 'comm_managers_staff',
    'comm_between_departments', 'comm_within_department',
    # Section 5
    'position_represented_properly', 'salary_competitive',
    'position_met_expectations', 'satisfied_performance_mgmt',
    'enjoyed_work', 'work_hours_reasonable', 'workload_reasonable',
    'sufficient_resources', 'familiar_disciplinary_procedures',
    'sufficient_professional_dev', 'satisfied_training_quality',
    'supervisors_helpful', 'would_recommend', 'would_rejoin',
    # Section 6
    'enjoyed_most', 'enjoyed_least', 'positive_aspects',
    'job_importance_extent', 'environment_rating', 'morale_rating',
    'coworker_relationship', 'supervisor_relationship',
    # Section 7
    'left_better_compensation', 'left_better_designation',
    'left_better_benefits', 'left_better_job_opportunity',
    'left_better_working_conditions', 'left_lack_of_recognition',
    'left_commuting_distance', 'left_difficult_supervisor',
    'left_no_advancement', 'left_family_circumstances',
    'left_moving_out_of_town', 'left_illness',
    'left_retirement', 'left_self_employment', 'last_project_worked',
    # Section 8
    'most_important_factor', 'could_prevent_leaving',
    'could_prevent_leaving_details', 'suggestions_for_improvement',
    'suggestions_details', 'anything_else', 'anything_else_details',
}

LEAVING_REASON_MAP = {
    'left_better_compensation': 'Better Compensation',
    'left_better_designation': 'Better Designation',
    'left_better_benefits': 'Better Benefits',
    'left_better_job_opportunity': 'Better Job Opportunity',
    'left_better_working_conditions': 'Better Working Conditions',
    'left_lack_of_recognition': 'Lack of Recognition for Work',
    'left_commuting_distance': 'Commuting Distance',
    'left_difficult_supervisor': 'Difficult with Supervisor',
    'left_no_advancement': 'No Advancement in Profile',
    'left_family_circumstances': 'Family Circumstances',
    'left_moving_out_of_town': 'Moving out of Town',
    'left_illness': 'Illness',
    'left_retirement': 'Retirement',
    'left_self_employment': 'Self-Employment',
}


def submit_exit_interview(interview, response_data):
    if interview.status == 'submitted':
        raise ValueError('Already submitted and cannot be edited.')

    clean_data = {
        k: v for k, v in response_data.items()
        if k in RESPONSE_FIELDS
    }

    ExitInterviewResponse.objects.create(
        exit_interview=interview,
        **clean_data,
    )

    # ── Increment ExitReason counters for checked reasons ──
    for field, reason_text in LEAVING_REASON_MAP.items():
        if clean_data.get(field) is True or clean_data.get(field) == 'true':
            reason, _ = ExitReason.objects.get_or_create(
                reason_text=reason_text,
                defaults={'is_predefined': True}
            )
            reason.counter += 1
            reason.save()

    # ── Also scan custom reason text ──
    custom_text = clean_data.get('most_important_factor', '')
    if custom_text:
        from apps.workforce.services.exit_reasons import extract_keywords_and_increment
        extract_keywords_and_increment(custom_text)

    interview.status       = 'submitted'
    interview.submitted_at = timezone.now()
    interview.save()

    create_notification(
    notif_type='exit_submitted',
    title='Exit Interview Submitted',
    message=f'{interview.employee.full_name} has completed the exit interview',
    link='/exit-interviews',
)

    return interview