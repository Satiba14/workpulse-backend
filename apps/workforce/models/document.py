import uuid
from django.db import models


class EmployeeDocumentMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_professional_details = models.ForeignKey(
        'workforce.EmployeeProfessionalDetails',
        on_delete=models.CASCADE,
        related_name='documents',   
    )

    name       = models.CharField(max_length=200)        
    unique_id  = models.CharField(max_length=50, unique=True)
    file_path  = models.CharField(max_length=1000, blank=True)  
    private_key = models.CharField(max_length=500, blank=True)
    public_key  = models.CharField(max_length=500, blank=True)
    deleted     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    document_type = models.CharField(
    max_length=20,
    choices=[
        ('photo', 'Photo'),
        ('resume', 'Resume'),
        ('offer_letter', 'Offer Letter'),
        ('revision_letter', 'Revision Letter'),
        ('other', 'Other'),
    ],
    default='other'
)

    class Meta:
        db_table = 'employee_document_master'

    def __str__(self):
        return f"{self.name} — {self.employee_professional_details.emp.full_name}"