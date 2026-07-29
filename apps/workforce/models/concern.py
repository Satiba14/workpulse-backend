import uuid
from django.db import models


class Concern(models.Model):
    """HR-initiated concern request sent to an employee."""

    STATUS_CHOICES = [
        ('open',       'Open'),
        ('in_review',  'In Review'),
        ('read',      'Read'),
        ('resolved',   'Resolved'),
    ]
    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]
    CATEGORY_CHOICES = [
        ('performance',  'Performance'),
        ('welfare',      'Welfare'),
        ('exit',         'Exit'),
        ('misconduct',   'Misconduct'),
        ('attendance',   'Attendance'),
        ('other',        'Other'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee        = models.ForeignKey(
        'workforce.Employee', on_delete=models.CASCADE, related_name='concerns'
    )
    created_by      = models.ForeignKey(
        'workforce.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_concerns'
    )
    reason_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    message         = models.TextField()                  # HR's message to employee
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority        = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    unique_token    = models.UUIDField(default=uuid.uuid4, unique=True)  # for employee response link
    email_sent_at   = models.DateTimeField(null=True, blank=True)
    reviewed_by     = models.ForeignKey(
        'workforce.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_concerns'
    )
    reminder_sent = models.BooleanField(default=False)
    deleted         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'concern_request'
        ordering = ['-created_at']

    def __str__(self):
        return f"Concern → {self.employee.full_name} [{self.status}]"


class ConcernResponse(models.Model):
    """Employee's private response to a concern request."""

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    concern          = models.OneToOneField(
        Concern, on_delete=models.CASCADE, related_name='response'
    )
    response_text    = models.TextField(blank=True)
    audio_file_path  = models.CharField(max_length=500, null=True, blank=True)
    document_file_path = models.CharField(max_length=500, null=True, blank=True)
    is_private       = models.BooleanField(default=True)
    responded_at     = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'concern_response'

    def __str__(self):
        return f"Response to {self.concern.id}"


class ConcernAccessLog(models.Model):
    """Tracks every time HR views an employee's response."""

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    concern_response = models.ForeignKey(
        ConcernResponse, on_delete=models.CASCADE, related_name='access_logs'
    )
    accessed_by      = models.ForeignKey(
        'workforce.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    accessed_at      = models.DateTimeField(auto_now_add=True)
    ip_address       = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'concern_access_log'
        ordering = ['-accessed_at']

    def __str__(self):
        return f"Access by {self.accessed_by} at {self.accessed_at}"