import uuid
from django.db import models


class ExitInterview(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('sent',      'Sent'),
        ('submitted', 'Submitted'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee     = models.OneToOneField(
        'workforce.Employee', on_delete=models.CASCADE, related_name='exit_interview'
    )
    token        = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at      = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    sent_by      = models.ForeignKey(
        'workforce.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    reminder_sent = models.BooleanField(default=False)
    deleted      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'exit_interviews'

    def __str__(self):
        return f"Exit Interview - {self.employee.full_name} ({self.status})"

    def get_unique_url(self):
        return f"/exit-interview/{self.employee.id}/{self.token}/"


RATING_CHOICES = [
    ('excellent', 'Excellent'),
    ('good',      'Good'),
    ('fair',      'Fair'),
    ('poor',      'Poor'),
]

SCALE_CHOICES = [
    ('very_good', 'Very Good'),
    ('good',      'Good'),
    ('average',   'Average'),
    ('poor',      'Poor'),
]


class ExitInterviewResponse(models.Model):
    """
    Matches Invenger's official Exit Interview Questionnaire (INV/HR/EIQ/v1.0).
    Restructured from boolean fields to match the full PDF form.
    """
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exit_interview = models.OneToOneField(
        ExitInterview, on_delete=models.CASCADE, related_name='response'
    )

    # ── Section 2: Reason for joining ────────────────────────────────────────
    joined_for_benefits        = models.BooleanField(default=False)
    joined_for_career          = models.BooleanField(default=False)
    joined_for_salary          = models.BooleanField(default=False)
    joined_for_reputation      = models.BooleanField(default=False)
    joined_for_other           = models.CharField(max_length=255, blank=True)

    # ── Section 3: Rating of Invenger ────────────────────────────────────────
    rating_company_benefits    = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    rating_salary              = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    rating_working_conditions  = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    rating_advancement         = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    rating_others              = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    rating_overall             = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)

    # ── Section 4: Communication rating ──────────────────────────────────────
    comm_throughout_company    = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    comm_managers_staff        = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    comm_between_departments   = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)
    comm_within_department     = models.CharField(max_length=20, choices=RATING_CHOICES, blank=True)

    # ── Section 5: Yes/No questions ───────────────────────────────────────────
    position_represented_properly  = models.BooleanField(null=True)
    salary_competitive             = models.BooleanField(null=True)
    position_met_expectations      = models.BooleanField(null=True)
    satisfied_performance_mgmt     = models.BooleanField(null=True)
    enjoyed_work                   = models.BooleanField(null=True)
    work_hours_reasonable          = models.BooleanField(null=True)
    workload_reasonable            = models.BooleanField(null=True)
    sufficient_resources           = models.BooleanField(null=True)
    familiar_disciplinary_procedures = models.BooleanField(null=True)
    sufficient_professional_dev    = models.BooleanField(null=True)
    satisfied_training_quality     = models.BooleanField(null=True)
    supervisors_helpful            = models.BooleanField(null=True)
    would_recommend                = models.BooleanField(null=True)
    would_rejoin                   = models.BooleanField(null=True)

    # ── Section 6: Open text + scale ratings ──────────────────────────────────
    enjoyed_most                   = models.TextField(blank=True)
    enjoyed_least                  = models.TextField(blank=True)
    positive_aspects               = models.TextField(blank=True)
    job_importance_extent          = models.TextField(blank=True)
    environment_rating             = models.CharField(max_length=20, choices=SCALE_CHOICES, blank=True)
    morale_rating                  = models.CharField(max_length=20, choices=SCALE_CHOICES, blank=True)
    coworker_relationship          = models.CharField(max_length=20, choices=SCALE_CHOICES, blank=True)
    supervisor_relationship        = models.CharField(max_length=20, choices=SCALE_CHOICES, blank=True)

    # ── Section 7: Primary reason for leaving (checkboxes) ────────────────────
    left_better_compensation       = models.BooleanField(default=False)
    left_better_designation        = models.BooleanField(default=False)
    left_better_benefits           = models.BooleanField(default=False)
    left_better_job_opportunity    = models.BooleanField(default=False)
    left_better_working_conditions = models.BooleanField(default=False)
    left_lack_of_recognition       = models.BooleanField(default=False)
    left_commuting_distance        = models.BooleanField(default=False)
    left_difficult_supervisor      = models.BooleanField(default=False)
    left_no_advancement            = models.BooleanField(default=False)
    left_family_circumstances      = models.BooleanField(default=False)
    left_moving_out_of_town        = models.BooleanField(default=False)
    left_illness                   = models.BooleanField(default=False)
    left_retirement                = models.BooleanField(default=False)
    left_self_employment           = models.BooleanField(default=False)
    last_project_worked            = models.CharField(max_length=255,blank=True)

    # ── Section 8: Final open questions ───────────────────────────────────────
    most_important_factor          = models.TextField(blank=True)
    could_prevent_leaving          = models.BooleanField(null=True)
    could_prevent_leaving_details  = models.TextField(blank=True)
    suggestions_for_improvement    = models.BooleanField(null=True)
    suggestions_details            = models.TextField(blank=True)
    anything_else                  = models.BooleanField(null=True)
    anything_else_details          = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    deleted      = models.BooleanField(default=False)

    class Meta:
        db_table = 'exit_interview_responses'

    def __str__(self):
        return f"Response - {self.exit_interview.employee.full_name}"