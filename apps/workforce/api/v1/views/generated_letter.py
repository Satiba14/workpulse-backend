import os
import uuid as uuid_lib
import base64

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from apps.workforce.models import Employee, GeneratedLetter
from apps.workforce.services.audit import create_audit_log


class GeneratedLetterCreateView(APIView):
    """
    POST /api/v1/employees/<pk>/generated-letters/
    Body: { file_base64, snapshot_data }
    Saves the generated .docx file to storage and creates an audit-trail record.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        file_base64   = request.data.get('file_base64')
        snapshot_data = request.data.get('snapshot_data', {})

        if not file_base64:
            return Response({'error': 'file_base64 is required'}, status=400)

        try:
            file_bytes = base64.b64decode(file_base64)
        except Exception:
            return Response({'error': 'Invalid file_base64 encoding'}, status=400)

        filename = f"{uuid_lib.uuid4()}.docx"
        rel_path = f"generated_letters/{pk}/{filename}"
        saved_path = default_storage.save(rel_path, ContentFile(file_bytes))
        media_url  = settings.MEDIA_URL.rstrip('/')
        file_url   = request.build_absolute_uri(f"{media_url}/{saved_path}")

        record = GeneratedLetter.objects.create(
            employee=employee,
            generated_by=request.user,
            file_path=file_url,
            snapshot_data=snapshot_data,
        )

        create_audit_log(
            user=request.user,
            action='create',
            model_name='GeneratedLetter',
            object_id=record.id,
            description=f'Generated Employee Details document for {employee.full_name}',
        )

        return Response({
            'id':         str(record.id),
            'file_path':  record.file_path,
            'created_at': record.created_at.isoformat(),
        }, status=201)

    def get(self, request, pk):
        """List past generated letters for this employee, most recent first."""
        records = GeneratedLetter.objects.filter(employee_id=pk).select_related('generated_by')
        return Response([
            {
                'id':            str(r.id),
                'file_path':     r.file_path,
                'created_at':    r.created_at.isoformat(),
                'generated_by':  r.generated_by.email if r.generated_by else None,
            }
            for r in records
        ])