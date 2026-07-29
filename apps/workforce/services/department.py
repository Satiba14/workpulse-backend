from django.db.models import Count, Q
from apps.workforce.models import (
    Department,
    Employee,
    ManagerDetails
)
from apps.workforce.services.audit import create_audit_log, get_client_ip

def get_all_departments(is_active=True):
    """
    Returns departments with all counts pre-calculated via SQL annotate().
    This fires exactly 1 query instead of 6 per department row.

    Annotations added:
      employee_count     — active employees (is_active=True)
      billable_count     — active + status='billable'
      non_billable_count — active + status='non_billable'
      buffer_count       — active + status='buffer'
      inactive_count     — active + status='inactive' (on-bench but not left)
      attrition_count    — left employees (is_active=False)
    """
    return Department.objects.filter(
        is_active=is_active
    ).select_related(
        'parent_department'
    ).annotate(
        employee_count=Count(
            'employees',
            filter=Q(employees__is_active=True),
            distinct=True
        ),
        billable_count=Count(
            'employees',
            filter=Q(employees__is_active=True, employees__status='billable'),
            distinct=True
        ),
        non_billable_count=Count(
            'employees',
            filter=Q(employees__is_active=True, employees__status='non_billable'),
            distinct=True
        ),
        buffer_count=Count(
            'employees',
            filter=Q(employees__is_active=True, employees__status='buffer'),
            distinct=True
        ),
        inactive_count=Count(
            'employees',
            filter=Q(employees__is_active=True, employees__status='inactive'),
            distinct=True
        ),
        attrition_count=Count(
            'employees',
            filter=Q(employees__is_active=False),
            distinct=True
        ),
    )


def get_department_by_id(pk):
    try:
        return Department.objects.select_related(
            'parent_department'
        ).annotate(
            employee_count=Count('employees', filter=Q(employees__is_active=True), distinct=True),
            billable_count=Count('employees', filter=Q(employees__is_active=True, employees__status='billable'), distinct=True),
            non_billable_count=Count('employees', filter=Q(employees__is_active=True, employees__status='non_billable'), distinct=True),
            buffer_count=Count('employees', filter=Q(employees__is_active=True, employees__status='buffer'), distinct=True),
            inactive_count=Count('employees', filter=Q(employees__is_active=True, employees__status='inactive'), distinct=True),
            attrition_count=Count('employees', filter=Q(employees__is_active=False), distinct=True),
        ).get(pk=pk), None
    except Department.DoesNotExist:
        return None, {'error': 'Department not found'}


def create_department(data, user, request):
    parent = data.get('parent_department')

    dept = Department.objects.create(
        name=data.get('name'),
        parent_department=parent,
    )
    manager_emp_id = data.get('manager_emp')

    if manager_emp_id:
        try:
            manager_emp = Employee.objects.get(id=manager_emp_id)

            ManagerDetails.objects.update_or_create(
                department=dept,
                defaults={
                    'emp': manager_emp,
                    'is_active': True
                }
            )
        except Employee.DoesNotExist:
            pass

    create_audit_log(
        user=user,
        action='create',
        model_name='Department',
        object_id=dept.id,
        description=f'Department {dept.name} created',
        ip_address=get_client_ip(request)
    )

    return dept


def update_department(dept, data, user, request):
    old_name = dept.name

    dept.name = data.get('name', dept.name)
    dept.is_active = data.get('is_active', dept.is_active)

    # ── PARENT DEPARTMENT ───────────────────────
    if 'parent_department' in data:
        parent_department_id = data.get('parent_department')

        if parent_department_id:
            dept.parent_department = Department.objects.get(
                id=parent_department_id
            )
        else:
            dept.parent_department = None

    dept.save()

    # ── MANAGER UPDATE ──────────────────────────
    manager_emp_id = data.get('manager_emp')

    if manager_emp_id:
        try:
            manager_emp = Employee.objects.get(id=manager_emp_id)
            dept.manager = manager_emp
            dept.save(update_fields=['manager'])

            ManagerDetails.objects.update_or_create(
                department=dept,
                defaults={
                    'emp': manager_emp,
                    'is_active': True
                }
            )

        except Employee.DoesNotExist:
            pass

    else:
        # remove manager if empty
        ManagerDetails.objects.filter(
            department=dept
        ).delete()

    create_audit_log(
        user=user,
        action='update',
        model_name='Department',
        object_id=dept.id,
        description=f'Department updated: {old_name} → {dept.name}',
        old_value=old_name,
        new_value=dept.name,
        ip_address=get_client_ip(request)
    )

    return dept


def delete_department(dept, user, request):
    name = dept.name
    dept.is_active = False
    dept.save()
    create_audit_log(
        user=user, action='delete', model_name='Department',
        object_id=dept.id,
        description=f'Department {name} deactivated',
        ip_address=get_client_ip(request)
    )