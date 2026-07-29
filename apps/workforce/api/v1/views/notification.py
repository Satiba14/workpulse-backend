from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.workforce.models.notification import Notification


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:30]
        return Response([
            {
                'id':          str(n.id),
                'type':        n.notif_type,
                'title':       n.title,
                'message':     n.message,
                'is_read':     n.is_read,
                'link':        n.link,
                'created_at':  n.created_at.isoformat(),
            }
            for n in notifs
        ])


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        if pk:
            # Mark single notification as read
            Notification.objects.filter(
                id=pk, user=request.user
            ).update(is_read=True)
        else:
            # Mark all as read
            Notification.objects.filter(
                user=request.user, is_read=False
            ).update(is_read=True)
        return Response({'success': True})


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({'count': count})