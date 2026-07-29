from apps.workforce.models import (
    Department, EmployeeProfessionalDetails,
    Concern, AttritionRecord
)


def get_dashboard_stats():
    all_prof = EmployeeProfessionalDetails.objects.all()
    total = all_prof.count()

    billable = all_prof.filter(status='billable').count()
    non_billable = all_prof.filter(status='non_billable').count()
    buffer = all_prof.filter(status='buffer').count()
    inactive = all_prof.filter(status='inactive').count()
    active = billable + non_billable + buffer

    open_concerns = Concern.objects.filter(
        status='open', deleted=False
    ).count()
    total_attrition = AttritionRecord.objects.filter(
        deleted=False
    ).count()

    departments_below = []
    for dept in Department.objects.filter(is_active=True):
        dept_total = all_prof.filter(department=dept).count()
        dept_buffer = all_prof.filter(
            department=dept, status='buffer'
        ).count()
        if dept_total > 0:
            buffer_pct = round((dept_buffer / dept_total * 100), 2)
            if buffer_pct < dept.buffer_threshold \
                    if hasattr(dept, 'buffer_threshold') else 10:
                needed = max(0, int(0.1 * dept_total) - dept_buffer)
                departments_below.append({
                    'department': dept.name,
                    'current_buffer_pct': buffer_pct,
                    'threshold': 10,
                    'employees_needed': needed,
                })

    attrition_rate = round(
        (inactive / total * 100), 2
    ) if total > 0 else 0

    return {
        'total_employees': total,
        'billable': billable,
        'non_billable': non_billable,
        'buffer': buffer,
        'inactive': inactive,
        'active': active,
        'total_attrition': total_attrition,
        'open_concerns': open_concerns,
        'attrition_rate': attrition_rate,
        'departments_below_buffer': departments_below,
    }