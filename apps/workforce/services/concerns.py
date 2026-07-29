from django.utils import timezone
from apps.workforce.models import Concern, ConcernResponse, ConcernAccessLog
from apps.workforce.services.audit import create_audit_log, get_client_ip
from common.logger import get_logger
import requests as http_requests
from django.conf import settings
from apps.workforce.services.notification import create_notification

logger = get_logger(__name__)

CATEGORIES = [
    'performance', 'welfare', 'exit',
    'misconduct', 'attendance', 'other',
]


def get_concerns(status=None, priority=None, category=None):
    qs = Concern.objects.select_related(
        'employee', 'created_by', 'reviewed_by', 'response'
    ).filter(deleted=False)
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if category:
        qs = qs.filter(reason_category=category)
    return qs


def get_concern_by_token(token):
    """Used by the public employee response form — no auth."""
    try:
        return Concern.objects.select_related('employee', 'response').get(
            unique_token=token, deleted=False
        )
    except Concern.DoesNotExist:
        return None


def create_concern(employee, created_by, category, message, priority='medium'):
    concern = Concern.objects.create(
        employee=employee,
        created_by=created_by,
        reason_category=category,
        message=message,
        priority=priority,
        status='open',
    )

    logger.info(
        f"Concern created for {employee.full_name} "
        f"by {created_by.email} [category={category}]"
    )

    # Send email via email-service webhook
    try:
        frontend_url = getattr(
            settings,
            'FRONTEND_URL',
            'http://localhost:5173'
        )

        response_url = (
            f"{frontend_url}/respond/{concern.unique_token}"
        )

        webhook_url = getattr(
            settings,
            'EMAIL_WEBHOOK_URL',
            'http://localhost:3001'
        )

        resp = http_requests.post(
            f"{webhook_url}/send-concern",
            json={
                'employee_name': employee.full_name,
                'employee_email': employee.email,
                'category': category,
                'message': message,
                'response_link': response_url,
            },
            timeout=5,
        )

        resp.raise_for_status()

        concern.email_sent_at = timezone.now()
        concern.save(update_fields=['email_sent_at'])

        logger.info(
            f"Concern email sent successfully to "
            f"{employee.email}"
        )

    except Exception as e:
        logger.warning(
            f"Email webhook failed: {e}"
        )

    create_notification(
    notif_type='concern_created',
    title='Feedback Request Sent',
    message=f'Feedback request sent to {employee.full_name} — {category}',
    link='/concerns',
)


    return concern


def resolve_concern(concern, reviewed_by, request=None):
    concern.status      = 'resolved'
    concern.reviewed_by = reviewed_by
    concern.save(update_fields=['status', 'reviewed_by', 'updated_at'])
    create_audit_log(
        user=reviewed_by,
        action='update',
        model_name='Concern',
        object_id=concern.id,
        description=f'Concern resolved for {concern.employee.full_name}',
        old_value='open',
        new_value='resolved',
        ip_address=get_client_ip(request) if request else None,
    )
    return concern


def submit_concern_response(concern, response_text='',
                             audio_file=None, document_file=None):
    """Called from the public (no-auth) employee response endpoint."""
    import os
    from django.conf import settings

    audio_path    = None
    document_path = None

    def save_file(f, subfolder):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'concern_responses', subfolder)
        os.makedirs(upload_dir, exist_ok=True)
        filename  = f"{uuid.uuid4()}_{f.name}"
        full_path = os.path.join(upload_dir, filename)
        with open(full_path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        return os.path.join('concern_responses', subfolder, filename)

    import uuid
    if audio_file:
        audio_path = save_file(audio_file, 'audio')
    if document_file:
        document_path = save_file(document_file, 'documents')

    # Update or create response
    response, _ = ConcernResponse.objects.update_or_create(
        concern=concern,
        defaults={
            'response_text':     response_text,
            'audio_file_path':   audio_path,
            'document_file_path': document_path,
        }
    )

    create_notification(
    notif_type='concern_response',
    title='Feedback Response Received',
    message=f'{concern.employee.full_name} has responded to the feedback request',
    link='/concerns',
)

    # Move concern to in_review once employee responds
    if concern.status == 'open':
        concern.status = 'in_review'
        concern.save(update_fields=['status', 'updated_at'])

    logger.info(f"Concern response submitted for concern {concern.id}")
    return response


def get_concern_response(concern, accessed_by, request=None):
    """HR views the response — logs the access."""
    try:
        response = concern.response
    except ConcernResponse.DoesNotExist:
        return None

    ConcernAccessLog.objects.create(
        concern_response=response,
        accessed_by=accessed_by,
        ip_address=get_client_ip(request) if request else None,
    )
    return response