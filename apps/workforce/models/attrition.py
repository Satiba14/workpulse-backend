import uuid
from django.db import models


class ExitReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reason_text = models.CharField(max_length=300)
    keywords = models.TextField(
        blank=True,
        help_text='Comma separated keywords for regex matching'
    )
    counter = models.IntegerField(default=0)
    is_predefined = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exit_reasons'
        ordering = ['-counter']

    def __str__(self):
        return f"{self.reason_text} (×{self.counter})"


class AttritionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        'workforce.Employee',
        on_delete=models.CASCADE,
        related_name='attrition_record'
    )
    exit_date = models.DateField()
    primary_reason = models.ForeignKey(
        ExitReason,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attrition_records'
    )
    custom_reason = models.TextField(blank=True)
    department = models.ForeignKey(
        'workforce.Department',
        on_delete=models.SET_NULL,
        null=True
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        'workforce.User',
        on_delete=models.SET_NULL,
        null=True
    )
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'attrition_records'
        ordering = ['-exit_date']

    def __str__(self):
        return f"{self.employee.full_name} exited on {self.exit_date}"