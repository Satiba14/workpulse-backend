import uuid
from django.db import models

class ManagerDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(
        'workforce.Department',
        on_delete=models.CASCADE,
        related_name='managers'
    )
    emp = models.ForeignKey(
        'workforce.Employee',
        on_delete=models.CASCADE,
        related_name='manager_roles'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manager_details'

    def __str__(self):
        return f"{self.emp.full_name} → {self.department.name}"