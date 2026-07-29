from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.workforce.services.audit import create_audit_log, get_client_ip

def login_user(request, email, password):
    user = authenticate(request, email=email, password=password)
    if not user:
        return None, {'error': 'Invalid credentials'}

    refresh = RefreshToken.for_user(user)
    create_audit_log(
        user=user,
        action='login',
        model_name='User',
        object_id=user.id,
        description=f'{user.email} logged in',
        ip_address=get_client_ip(request)
    )
    return user, {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name,
            'phone': user.phone,
            'designation': user.designation,
        }
    }


def logout_user(request, refresh_token, user=None):
    try:
        audit_user = user or request.user
        print("DEBUG LOGOUT - user:", audit_user)
        print("DEBUG LOGOUT - refresh_token:", refresh_token)
        create_audit_log(
            user=audit_user,
            action='logout',
            model_name='User',
            object_id=audit_user.id,
            description=f'{audit_user.email} logged out',
            ip_address=get_client_ip(request)
        )
        print("DEBUG LOGOUT - audit log saved OK")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True, {'message': 'Logged out successfully'}
    except Exception as e:
        print("DEBUG LOGOUT ERROR:", e)
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}