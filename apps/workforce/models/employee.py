import uuid
from django.db import models

class Employee(models.Model):
    GENDER_CHOICES    = [('male','Male'),('female','Female'),('other','Other')]
    BLOOD_CHOICES     = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                         ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')]
    MARITAL_CHOICES   = [('single','Single'),('married','Married'),
                         ('divorced','Divorced'),('widowed','Widowed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ── Personal ───────────────────────────────────────────────────────────────
    first_name            = models.CharField(max_length=100)
    last_name             = models.CharField(max_length=100)
    phone_no              = models.CharField(max_length=15)
    email                = models.EmailField(max_length=255, null=True, blank=True)
    alternative_phone_no  = models.CharField(max_length=15, blank=True)
    date_of_birth         = models.DateField(null=True, blank=True)
    gender                = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group           = models.CharField(max_length=5,  choices=BLOOD_CHOICES,  blank=True)
    marital_status        = models.CharField(max_length=15, choices=MARITAL_CHOICES,blank=True)

    # ── Address (split into current / permanent / aadhaar) ─────────────────────
    current_address   = models.TextField(blank=True)
    current_pincode   = models.CharField(max_length=10, blank=True)
    current_city      = models.CharField(max_length=100, blank=True)
    current_state     = models.CharField(max_length=100, blank=True)

    permanent_address = models.TextField(blank=True)
    permanent_pincode = models.CharField(max_length=10, blank=True)
    permanent_city    = models.CharField(max_length=100, blank=True)
    permanent_state   = models.CharField(max_length=100, blank=True)

    aadhaar_address   = models.TextField(blank=True)
    nation            = models.CharField(max_length=100, blank=True)

    # ── Legacy fields kept for backward compat (can be removed after migration) ─
    address  = models.TextField(blank=True)
    pincode  = models.IntegerField(null=True, blank=True)
    state    = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)

    # ── Family ─────────────────────────────────────────────────────────────────
    father_name                = models.CharField(max_length=150, blank=True)
    mother_name                = models.CharField(max_length=150, blank=True)
    spouse_name                = models.CharField(max_length=150, blank=True)
    emergency_contact_name     = models.CharField(max_length=150, blank=True)
    emergency_contact_phone    = models.CharField(max_length=15,  blank=True)
    emergency_contact_relation = models.CharField(max_length=50,  blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class EmployeeProfessionalDetails(models.Model):
    STATUS_CHOICES = [
        ('billable','Billable'), ('non_billable','Non-Billable'),
        ('buffer','Buffer'),     ('inactive','Inactive'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emp = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='professional_details')
    department   = models.ForeignKey('workforce.Department', on_delete=models.SET_NULL,
                                     null=True, related_name='employees')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='billable')
    reporting_to = models.ForeignKey(
    'workforce.Employee',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='reportees'
)
    joined_on    = models.DateField(null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)

    last_project_worked = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    designation = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'employee_professional_details'

    def __str__(self):
        return f"{self.emp.full_name} — Professional"