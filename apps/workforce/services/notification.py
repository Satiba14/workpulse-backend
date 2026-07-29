from apps.workforce.models.notification import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(notif_type, title, message, link=''):
    """
    Creates a notification for ALL HR/admin users.
    """
    hr_users = User.objects.filter(is_active=True)
    notifications = [
        Notification(
            user=user,
            notif_type=notif_type,
            title=title,
            message=message,
            link=link,
        )
        for user in hr_users
    ]
    Notification.objects.bulk_create(notifications)