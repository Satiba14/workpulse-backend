import requests as http_requests
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from apps.workforce.models import ExitInterview, Concern
from apps.workforce.services.notification import create_notification

from common.logger import get_logger

logger = get_logger(__name__)

EMAIL_WEBHOOK_URL = getattr(settings, 'EMAIL_WEBHOOK_URL', 'http://localhost:3001')
FRONTEND_URL       = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')


class Command(BaseCommand):
    help = "Send one-time automatic reminders for pending exit interviews and feedback requests."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=1)

        exit_count    = self.remind_exit_interviews(cutoff)
        concern_count = self.remind_concerns(cutoff)

        self.stdout.write(self.style.SUCCESS(
            f"Reminders sent — Exit Interviews: {exit_count}, Feedback Requests: {concern_count}"
        ))

    # ── Exit Interview reminders ────────────────────────────────────────────
    def remind_exit_interviews(self, cutoff):
        pending = ExitInterview.objects.filter(
            status='sent',
            sent_at__lte=cutoff,
            reminder_sent=False,
        ).select_related('employee')

        sent = 0
        for interview in pending:
            employee = interview.employee
            if not employee.email:
                continue

            form_url = f"{FRONTEND_URL}/exit-interview/{employee.id}/{interview.token}"

            try:
                resp = http_requests.post(
                    f"{EMAIL_WEBHOOK_URL}/send-exit-interview-reminder",
                    json={
                        'employee_name':  employee.full_name,
                        'employee_email': employee.email,
                        'form_link':      form_url,
                    },
                    timeout=5,
                )
                if resp.ok:
                    interview.reminder_sent = True
                    interview.save(update_fields=['reminder_sent'])
                    sent += 1
                    logger.info(f"Exit interview reminder sent to {employee.email}")

                    create_notification(
                        notif_type='exit_submitted',
                        title='Reminder Sent',
                        message=f'Automatic reminder sent to {employee.full_name} for exit interview',
                        link='/exit-interviews',
                    )
                else:
                    logger.warning(f"Reminder webhook failed for {employee.email}: {resp.text}")
            except Exception as e:
                logger.warning(f"Exit interview reminder failed for {employee.email}: {e}")

        return sent

    # ── Concern / Feedback reminders ────────────────────────────────────────
    def remind_concerns(self, cutoff):
        pending = Concern.objects.filter(
            status__in=['open', 'in_progress'],
            created_at__lte=cutoff,
            reminder_sent=False,
            deleted=False,
        ).select_related('employee')

        sent = 0
        for concern in pending:
            employee = concern.employee
            if not employee or not employee.email:
                continue

            response_url = f"{FRONTEND_URL}/respond/{concern.unique_token}"

            try:
                resp = http_requests.post(
                    f"{EMAIL_WEBHOOK_URL}/send-concern-reminder",
                    json={
                        'employee_name':  employee.full_name,
                        'employee_email': employee.email,
                        'category':       concern.reason_category,
                        'message':        concern.message,
                        'response_link':  response_url,
                    },
                    timeout=5,
                )
                if resp.ok:
                    concern.reminder_sent = True
                    concern.save(update_fields=['reminder_sent'])
                    sent += 1
                    logger.info(f"Feedback reminder sent to {employee.email}")

                    create_notification(
                        notif_type='concern_created',
                        title='Reminder Sent',
                        message=f'Automatic reminder sent to {employee.full_name} for feedback request',
                        link='/concerns',
                    )
                else:
                    logger.warning(f"Reminder webhook failed for {employee.email}: {resp.text}")
            except Exception as e:
                logger.warning(f"Feedback reminder failed for {employee.email}: {e}")

        return sent