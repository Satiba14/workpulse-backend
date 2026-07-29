import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    TYPE_CHOICES = [
        ('concern_response',   'Concern Response Received'),
        ('exit_submitted',     'Exit Interview Submitted'),
        ('concern_created',    'Feedback Request Sent'),
        ('employee_inactive',  'Employee Marked Inactive'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type  = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title       = models.CharField(max_length=255)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    link        = models.CharField(max_length=255, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notif_type} — {self.title}"