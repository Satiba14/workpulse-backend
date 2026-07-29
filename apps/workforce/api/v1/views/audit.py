from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.workforce.models import AuditLog
from apps.workforce.serializers.audit import AuditLogSerializer


class AuditLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AuditLog.objects.select_related('user').all()
        action = request.query_params.get('action')
        model = request.query_params.get('model')
        if action:
            logs = logs.filter(action__iexact=action)
        if model:
            logs = logs.filter(model_name=model)
        return Response(
            AuditLogSerializer(logs[:100], many=True).data
        )