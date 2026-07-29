import uuid
from django.db import models

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    manager = models.ForeignKey(
    'workforce.Employee',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='managed_departments'
)
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sub_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department_details'

    def __str__(self):
        return self.name