from apps.workforce.models import AuditLog


def create_audit_log(user, action, model_name,
                     object_id='', description='',
                     old_value='', new_value='',
                     ip_address=None):
    AuditLog.objects.create(
        user=user, action=action,
        model_name=model_name,
        object_id=str(object_id),
        description=description,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address
    )


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')