"""
Management command to seed AttritionRecord entries from existing
inactive employees who don't have one yet.

Usage:
    python manage.py seed_attrition_records
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.workforce.models import (
    EmployeeProfessionalDetails, AttritionRecord
)


class Command(BaseCommand):
    help = 'Creates AttritionRecord entries for inactive employees missing one'

    def handle(self, *args, **options):
        inactive = EmployeeProfessionalDetails.objects.filter(
            status='inactive'
        ).select_related('emp', 'department')

        created = 0
        skipped = 0

        for prof in inactive:
            # skip if record already exists
            if AttritionRecord.objects.filter(employee=prof.emp).exists():
                skipped += 1
                continue

            # use updated_at as exit_date approximation
            exit_date = (
                prof.updated_at.date()
                if prof.updated_at
                else timezone.now().date()
            )

            AttritionRecord.objects.create(
                employee=prof.emp,
                exit_date=exit_date,
                department=prof.department,
                custom_reason='Migrated from inactive status',
                deleted=False,
            )
            created += 1
            self.stdout.write(
                f'  Created record for {prof.emp.full_name} '
                f'(exit: {exit_date})'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone — {created} records created, {skipped} skipped.'
            )
        )