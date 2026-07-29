from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q
from apps.workforce.models import AttritionRecord, EmployeeProfessionalDetails
from .exit_reasons import get_top_exit_reasons


def get_attrition_analytics(months: int = 12) -> dict:
    today      = date.today()
    start_date = today - relativedelta(months=months)

    # ── Fetch ALL records once, no lazy per-loop queries ─────────────────────
    records = list(
        AttritionRecord.objects
        .select_related(
            'employee__professional_details',
            'department',
            'primary_reason',
        )
        .filter(deleted=False, exit_date__gte=start_date)
    )

    # ── 1. Monthly trend — pure Python, zero extra DB hits ───────────────────
    # Fetch ALL professional details once
    all_prof = list(
        EmployeeProfessionalDetails.objects
        .values('joined_on')
    )

    # Build lookup sets in memory
    exit_by_month = {}     # 'YYYY-MM' → count
    for r in records:
        key = r.exit_date.strftime('%Y-%m')
        exit_by_month[key] = exit_by_month.get(key, 0) + 1

    join_by_month = {}     # 'YYYY-MM' → count
    for p in all_prof:
        if p['joined_on']:
            key = p['joined_on'].strftime('%Y-%m')
            join_by_month[key] = join_by_month.get(key, 0) + 1

    # Total headcount before the window
    start_hc_base = sum(
        1 for p in all_prof
        if p['joined_on'] and p['joined_on'] < (today - relativedelta(months=months)).replace(day=1)
    )

    monthly_trend = []
    running_hc = start_hc_base

    for i in range(months):
        month_start = (today - relativedelta(months=months - 1 - i)).replace(day=1)
        key         = month_start.strftime('%Y-%m')
        label       = month_start.strftime('%b %Y')

        joiners  = join_by_month.get(key, 0)
        leavers  = exit_by_month.get(key, 0)
        end_hc   = max(0, running_hc + joiners - leavers)
        avg_hc   = (running_hc + end_hc) / 2
        rate     = round((leavers / avg_hc * 100), 2) if avg_hc > 0 else 0

        monthly_trend.append({
            'month':    label,
            'joiners':  joiners,
            'leavers':  leavers,
            'start_hc': running_hc,
            'end_hc':   end_hc,
            'rate':     rate,
        })
        running_hc = end_hc

    # ── 2. By department — one aggregation query ──────────────────────────────
    # Get all dept headcounts in ONE query
    dept_headcounts = dict(
        EmployeeProfessionalDetails.objects
        .values('department_id')
        .annotate(total=Count('id'))
        .values_list('department_id', 'total')
    )

    dept_map = {}
    for r in records:
        dept_id   = r.department_id
        dept_name = r.department.name if r.department else 'Unknown'

        if dept_name not in dept_map:
            dept_map[dept_name] = {
                'exits':     0,
                'headcount': dept_headcounts.get(dept_id, 0),
            }
        dept_map[dept_name]['exits'] += 1

    by_department = sorted(
        [
            {
                'department': name,
                'exits':      v['exits'],
                'headcount':  v['headcount'],
                'rate':       round((v['exits'] / v['headcount']) * 100, 1)
                              if v['headcount'] > 0 else 0,
            }
            for name, v in dept_map.items()
        ],
        key=lambda x: x['exits'],
        reverse=True,
    )

    # ── 3. By designation — pure Python from already-loaded records ───────────
    desig_map: dict[str, int] = {}
    for r in records:
        try:
            desig = r.employee.professional_details.designation or 'Not specified'
        except Exception:
            desig = 'Not specified'
        desig_map[desig] = desig_map.get(desig, 0) + 1

    by_designation = [
        {'designation': k, 'exits': v}
        for k, v in sorted(desig_map.items(), key=lambda x: -x[1])
        if k != 'Not specified'
    ]
    if desig_map.get('Not specified'):
        by_designation.append({
            'designation': 'Not specified',
            'exits':       desig_map['Not specified'],
        })

    # ── 4. By experience — pure Python ───────────────────────────────────────
    exp_buckets = {'0–2 yrs': 0, '3–5 yrs': 0, '6–10 yrs': 0, '10+ yrs': 0}
    for r in records:
        try:
            joined = r.employee.professional_details.joined_on
            if joined:
                years = (r.exit_date - joined).days / 365.25
                if years <= 2:
                    exp_buckets['0–2 yrs']  += 1
                elif years <= 5:
                    exp_buckets['3–5 yrs']  += 1
                elif years <= 10:
                    exp_buckets['6–10 yrs'] += 1
                else:
                    exp_buckets['10+ yrs']  += 1
        except Exception:
            pass

    by_experience = [{'bucket': k, 'exits': v} for k, v in exp_buckets.items()]

    # ── 5. Top exit reasons (all-time) ────────────────────────────────────────
    top_exit_reasons = get_top_exit_reasons(limit=10)

    return {
        'monthly_trend':    monthly_trend,
        'by_department':    by_department,
        'by_designation':   by_designation,
        'by_experience':    by_experience,
        'top_exit_reasons': top_exit_reasons,
    }