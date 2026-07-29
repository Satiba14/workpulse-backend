from datetime import date
from apps.workforce.models import Employee, EmployeeProfessionalDetails, AttritionRecord
from apps.workforce.services.audit import create_audit_log, get_client_ip

from common.logger import get_logger
from apps.workforce.services.notification import create_notification

logger = get_logger(__name__)

PERSONAL_FIELDS = [
    'first_name', 'last_name', 'phone_no','email', 'alternative_phone_no',
    'date_of_birth', 'gender', 'blood_group', 'marital_status',
    'current_address', 'current_pincode', 'current_city', 'current_state',
    'permanent_address', 'permanent_pincode', 'permanent_city', 'permanent_state',
    'aadhaar_address', 'nation',
    'father_name', 'mother_name', 'spouse_name',
]

TRULY_NULLABLE = {'date_of_birth'}

TEXT_FIELDS = {
    'gender', 'blood_group', 'marital_status',
    'father_name', 'mother_name', 'spouse_name',
    'current_address', 'current_pincode', 'current_city', 'current_state',
    'permanent_address', 'permanent_pincode', 'permanent_city', 'permanent_state',
    'aadhaar_address', 'nation',
    'alternative_phone_no',
}


def _safe_value(field, value):
    if field in TRULY_NULLABLE:
        return value if value else None
    if field in TEXT_FIELDS:
        return value if value is not None else ''
    return value


def get_all_employees(filters=None):
    employees = Employee.objects.select_related(
    'professional_details__department',
    'professional_details__reporting_to').filter(
    professional_details__is_active=True
)

    if not filters:
        return employees

    search = filters.get('search')
    dept   = filters.get('department')
    status = filters.get('status')

    if search:
        from django.db.models import Q
        employees = employees.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if dept:
        employees = employees.filter(professional_details__department_id=dept)
    if status:
        if status == 'inactive':
            employees = employees.filter( 
                professional_details__is_active=False
            )
        else:
            employees = employees.filter(professional_details__status=status)
    return employees


def get_employee_by_id(pk):
    try:
        return Employee.objects.select_related(
            'professional_details__department',
            'professional_details__reporting_to',
        ).prefetch_related(
            'professional_details__documents'
        ).get(pk=pk), None
    except Employee.DoesNotExist:
        return None, {'error': 'Employee not found'}


def create_employee(data, user, request):
    logger.info(
        f"Creating employee: {data.get('first_name')} {data.get('last_name')} — by {user.email}"
    )
    try:
        emp_data = {
            f: _safe_value(f, data.get(f, ''))
            for f in PERSONAL_FIELDS
        }
        emp = Employee.objects.create(**emp_data)

        reporting_to_id = data.get('reporting_to')
        reporting_to = None
        if reporting_to_id:
            reporting_to = Employee.objects.filter(id=reporting_to_id).first()

        EmployeeProfessionalDetails.objects.create(
            emp=emp,
            department_id=data.get('department') or None,
            designation=data.get('designation', ''),
            joined_on=data.get('joined_on') or None,
            reporting_to=reporting_to,
            status=data.get('status', 'billable'),
            is_active=True,
        )

        create_audit_log(
            user=user,
            action='create',
            model_name='Employee',
            object_id=emp.id,
            description=f'Employee {emp.full_name} created',
            ip_address=get_client_ip(request)
        )

        logger.info(f"Employee created successfully: {emp.id}")
        return emp

    except Exception as e:
        logger.error(f"Failed to create employee: {e}", exc_info=True)
        raise


def update_employee(emp, data, user, request):
    for field in PERSONAL_FIELDS:
        if field in data:
            setattr(emp, field, _safe_value(field, data[field]))
    emp.save()

    prof = getattr(emp, 'professional_details', None)
    if prof:
        old_status = prof.status  # ← capture before update

        if 'department'   in data: prof.department_id = data['department'] or None
        if 'designation'  in data: prof.designation   = data['designation'] or ''
        if 'joined_on'    in data: prof.joined_on     = data['joined_on']  or None
        if 'is_active'    in data: prof.is_active      = data['is_active']
        if 'reporting_to' in data:
            reporting_to_id = data.get('reporting_to')
            prof.reporting_to = (
                Employee.objects.filter(id=reporting_to_id).first()
                if reporting_to_id else None
            )
        if 'status' in data:
            prof.status = data['status']

        prof.save()

        # ── Auto-create AttritionRecord when status changes to inactive ──────
        new_status = data.get('status')
        if new_status == 'inactive' and old_status != 'inactive':
            if not AttritionRecord.objects.filter(employee=emp).exists():
                AttritionRecord.objects.create(
                    employee=emp,
                    exit_date=date.today(),
                    department=prof.department,
                    custom_reason='Status changed to inactive',
                    deleted=False,
                )
                create_notification(
                    notif_type='employee_inactive',
                    title='Employee Marked Inactive',
                    message=f'{emp.full_name} has been marked as inactive',
                    link='/employees',
                )
                logger.info(
                    f"AttritionRecord auto-created for {emp.full_name} "
                    f"(status: {old_status} → inactive)"
                )

    create_audit_log(
        user=user, action='update', model_name='Employee',
        object_id=emp.id,
        description=f'Employee {emp.full_name} updated',
        ip_address=get_client_ip(request)
    )
    return emp


def delete_employee(emp, user, request):
    prof = getattr(emp, 'professional_details', None)
    if prof:
        old_status = prof.status
        prof.is_active = False
        prof.save()

        # ── Auto-create AttritionRecord on delete/deactivate too ─────────────
        if old_status != 'inactive':
            if not AttritionRecord.objects.filter(employee=emp).exists():
                AttritionRecord.objects.create(
                    employee=emp,
                    exit_date=date.today(),
                    department=prof.department,
                    custom_reason='Employee deactivated',
                    deleted=False,
                )
                logger.info(f"AttritionRecord auto-created on deactivation: {emp.full_name}")

    create_audit_log(
        user=user, action='delete', model_name='Employee',
        object_id=emp.id,
        description=f'Employee {emp.full_name} deactivated',
        ip_address=get_client_ip(request)
    )