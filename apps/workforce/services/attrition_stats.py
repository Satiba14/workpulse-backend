from apps.workforce.models import Department, EmployeeProfessionalDetails


def get_attrition_stats():
    """
    Returns overall attrition rate and per-department breakdown.
    Used by the dashboard and the stats API endpoint.
    """
    all_prof = EmployeeProfessionalDetails.objects.all()
    total    = all_prof.count()
    inactive = all_prof.filter(status='inactive').count()
    overall_rate = round((inactive / total * 100), 2) if total > 0 else 0

    by_dept = []
    for dept in Department.objects.filter(is_active=True):
        dept_total    = all_prof.filter(department=dept).count()
        dept_inactive = all_prof.filter(department=dept, status='inactive').count()
        rate = round((dept_inactive / dept_total * 100), 2) if dept_total > 0 else 0
        by_dept.append({
            'department':     dept.name,
            'total':          dept_total,
            'inactive':       dept_inactive,
            'attrition_rate': rate,
        })

    return {
        'overall_rate':   overall_rate,
        'total_inactive': inactive,
        'by_department':  by_dept,
    }