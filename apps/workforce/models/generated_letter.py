import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GeneratedLetter(models.Model):
    """
    Stores a record every time HR generates an Employee Details document
    from the Employee Documents page. Keeps the actual file so it can be
    re-downloaded later, and the snapshot of data used to fill it in case
    the employee's record changes afterward.
    """
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee      = models.ForeignKey(
        'workforce.Employee',
        on_delete=models.CASCADE,
        related_name='generated_letters',
    )
    generated_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_path     = models.CharField(max_length=1000, blank=True)
    snapshot_data = models.JSONField(default=dict, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'generated_letter'
        ordering = ['-created_at']

    def __str__(self):
        return f"Letter for {self.employee.full_name} — {self.created_at.strftime('%d %b %Y')}"