import re
from apps.workforce.models import ExitReason
# ── Keyword → canonical reason text mapping ───────────────────────────────────
KEYWORD_MAP = {
    'manager':     'Manager pressure / toxic manager',
    'salary':      'Salary dissatisfaction',
    'growth':      'No growth opportunity',
    'leave':       'Work-life balance / leave issues',
    'workload':    'Workload / burnout',
    'opportunity': 'Better opportunity elsewhere',
    'relocation':  'Relocation / personal',
}


def extract_keywords_and_increment(text: str) -> list[str]:
    """
    Scans free-text for known keywords, increments matching ExitReason
    counters, and returns a list of matched reason texts.
    """
    text_lower = text.lower()
    matched = set()

    for keyword, reason_text in KEYWORD_MAP.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            matched.add(reason_text)

    for reason_text in matched:
        reason, _ = ExitReason.objects.get_or_create(
            reason_text=reason_text,
            defaults={'is_predefined': True}
        )
        reason.counter += 1
        reason.save()

    return list(matched)


def get_top_exit_reasons(limit: int = 10) -> list[dict]:
    """
    Returns the top N exit reasons ordered by frequency.
    """
    reasons = ExitReason.objects.filter(
        counter__gt=0, deleted=False
    ).order_by('-counter')[:limit]

    total = sum(r.counter for r in reasons)

    return [
        {
            'id':          str(r.id),
            'reason_text': r.reason_text,
            'count':       r.counter,
            'percentage':  round((r.counter / total * 100), 2) if total > 0 else 0,
        }
        for r in reasons
    ]