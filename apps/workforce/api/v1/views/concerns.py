from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from apps.workforce.models import Concern, Employee
from apps.workforce.serializers.concerns import ConcernSerializer, ConcernResponseSerializer
from apps.workforce.services.concerns import (
    get_concerns, get_concern_by_token,
    create_concern, resolve_concern,
    submit_concern_response, get_concern_response,
)


class ConcernListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        concerns = get_concerns(
            status=request.query_params.get('status'),
            priority=request.query_params.get('priority'),
            category=request.query_params.get('category'),
        )
        return Response(ConcernSerializer(concerns, many=True).data)

    def post(self, request):
        employee_id = request.data.get('employee')
        category    = request.data.get('reason_category')
        message     = request.data.get('message')
        priority    = request.data.get('priority', 'medium')

        if not employee_id or not category or not message:
            return Response(
                {'error': 'employee, reason_category and message are required.'},
                status=400
            )
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=404)

        concern = create_concern(
            employee=employee,
            created_by=request.user,
            category=category,
            message=message,
            priority=priority,
        )
        return Response(ConcernSerializer(concern).data, status=201)


class ConcernDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        concern = get_object_or_404(Concern, pk=pk, deleted=False)
        return Response(ConcernSerializer(concern).data)

    def put(self, request, pk):
        concern = get_object_or_404(Concern, pk=pk, deleted=False)
        action  = request.data.get('action')

        if action == 'read':
            # HR viewed the response — mark as read
            concern.status      = 'read'
            concern.reviewed_by = request.user
            concern.save(update_fields=['status', 'reviewed_by', 'updated_at'])

        elif action == 'resolve':
            concern = resolve_concern(
                concern=concern,
                reviewed_by=request.user,
                request=request,
            )
        else:
            return Response({'error': 'Unknown action. Use "read" or "resolve".'}, status=400)

        return Response(ConcernSerializer(concern).data)

    def delete(self, request, pk):
        concern = get_object_or_404(Concern, pk=pk, deleted=False)
        concern.deleted = True
        concern.save(update_fields=['deleted'])
        return Response(status=204)


class ConcernResponseView(APIView):
    """HR views the employee's response — access is logged."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        concern  = get_object_or_404(Concern, pk=pk, deleted=False)
        response = get_concern_response(
            concern=concern,
            accessed_by=request.user,
            request=request,
        )
        if not response:
            return Response({'error': 'No response yet.'}, status=404)
        return Response(ConcernResponseSerializer(response).data)


class PublicConcernRespondView(APIView):
    """Public — no auth. Employee opens link and submits response."""
    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, token):
        concern = get_concern_by_token(token)
        if not concern:
            return Response({'error': 'Invalid or expired link.'}, status=404)

        try:
            already_responded = concern.response is not None
        except Exception:
            already_responded = False

        return Response({
            'employee_name':     concern.employee.full_name,
            'reason_category':   concern.reason_category,
            'message':           concern.message,
            'status':            concern.status,
            'already_responded': already_responded,
        })

    def post(self, request, token):
        concern = get_concern_by_token(token)
        if not concern:
            return Response({'error': 'Invalid or expired link.'}, status=404)

        if concern.status == 'resolved':
            return Response({'error': 'This concern has already been resolved.'}, status=400)

        try:
            already = concern.response is not None
            if already:
                return Response({'error': 'You have already submitted a response.'}, status=400)
        except Exception:
            pass

        response = submit_concern_response(
            concern=concern,
            response_text=request.data.get('response_text', ''),
            audio_file=request.FILES.get('audio_file'),
            document_file=request.FILES.get('document_file'),
        )
        return Response(ConcernResponseSerializer(response).data, status=201)