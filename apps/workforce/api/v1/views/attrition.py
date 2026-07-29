from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.workforce.models import ExitReason, AttritionRecord
from apps.workforce.serializers.attrition import (
    AttritionRecordSerializer, ExitReasonSerializer,
)
from apps.workforce.services import (
    get_attrition_stats, get_top_exit_reasons, get_attrition_analytics,
)


class AttritionStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_attrition_stats())


class AttritionAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        months = int(request.query_params.get('months', 12))
        months = max(1, min(months, 60))
        return Response(get_attrition_analytics(months=months))


class AttritionRecordListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = AttritionRecord.objects.select_related(
            'employee', 'department', 'primary_reason'
        ).filter(deleted=False)
        return Response(AttritionRecordSerializer(records, many=True).data)

    def post(self, request):
        serializer = AttritionRecordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            record = serializer.save()
            return Response(AttritionRecordSerializer(record).data, status=201)
        return Response(serializer.errors, status=400)


class ExitReasonListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reasons = ExitReason.objects.filter(
            deleted=False
        ).order_by('-counter')
        return Response(ExitReasonSerializer(reasons, many=True).data)


class TopExitReasonsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        return Response(get_top_exit_reasons(limit=limit))