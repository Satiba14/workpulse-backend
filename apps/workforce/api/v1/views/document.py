import os
import uuid as uuid_lib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from apps.workforce.models import EmployeeDocumentMaster, EmployeeProfessionalDetails

ALLOWED_EXTENSIONS = {
    '.pdf', '.png', '.jpg', '.jpeg', '.webp', '.svg',
    '.doc', '.docx',
}


class EmployeeDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, pk):
        try:
            prof = EmployeeProfessionalDetails.objects.get(emp_id=pk)
        except EmployeeProfessionalDetails.DoesNotExist:
            return Response({'error': 'Employee professional details not found'}, status=404)

        doc_name      = request.data.get('name', 'Document')
        file          = request.FILES.get('file')
        document_type = request.data.get('document_type', 'other')

        if not file:
            return Response({'error': 'No file provided. Send file in multipart field "file".'}, status=400)

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {'error': 'Only PDF, PNG, JPG, JPEG, WEBP, SVG, DOC and DOCX files are allowed.'},
                status=400
            )

        filename = f"{uuid_lib.uuid4()}{ext}"
        rel_path = f"employee_docs/{pk}/{filename}"

        saved_path = default_storage.save(rel_path, ContentFile(file.read()))
        media_url  = settings.MEDIA_URL.rstrip('/')
        file_url   = request.build_absolute_uri(f"{media_url}/{saved_path}")

        # ── Replace existing document of the SAME type instead of duplicating ──
        existing = EmployeeDocumentMaster.objects.filter(
            employee_professional_details=prof,
            document_type=document_type,
            deleted=False,
        ).first()

        if existing:
            # Optionally remove old physical file from storage
            try:
                old_rel_path = existing.file_path.split(media_url, 1)[-1].lstrip('/')
                if old_rel_path and default_storage.exists(old_rel_path):
                    default_storage.delete(old_rel_path)
            except Exception:
                pass  # don't block the update if old file cleanup fails

            existing.name      = doc_name
            existing.file_path = file_url
            existing.unique_id = str(uuid_lib.uuid4())[:8].upper()
            existing.save()
            doc = existing
            status_code = 200
        else:
            doc = EmployeeDocumentMaster.objects.create(
                employee_professional_details=prof,
                name=doc_name,
                file_path=file_url,
                unique_id=str(uuid_lib.uuid4())[:8].upper(),
                document_type=document_type,
                deleted=False,
            )
            status_code = 201

        return Response({
            'id':            str(doc.id),
            'name':          doc.name,
            'unique_id':     doc.unique_id,
            'file_path':     doc.file_path,
            'document_type': doc.document_type,
            'deleted':       doc.deleted,
        }, status=status_code)

    def delete(self, request, pk, doc_id):
        """Soft-delete a document."""
        try:
            doc = EmployeeDocumentMaster.objects.get(pk=doc_id)
            doc.deleted = True
            doc.save()
            return Response(status=204)
        except EmployeeDocumentMaster.DoesNotExist:
            return Response({'error': 'Document not found'}, status=404)