import base64
import requests as http_requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.workforce.models import Employee, EmployeeDocumentMaster


class EmployeeLetterDataView(APIView):
    """
    GET /api/v1/employees/<pk>/letter-data/
    Returns all employee fields needed to pre-fill the
    Employee Details document, including the photo (base64)
    if one has been uploaded.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            emp = Employee.objects.select_related(
                'professional_details__department',
                'professional_details__reporting_to',
            ).get(pk=pk)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        prof = getattr(emp, 'professional_details', None)

        data = {
            'first_name':     emp.first_name,
            'last_name':      emp.last_name,
            'emp_id':         str(emp.id)[:8].upper(),
            'email':          emp.email or '',
            'official_email': emp.email or '',   # update if you add a separate official email field later
            'department':     prof.department.name if prof and prof.department else '',
            'reporting_to':   prof.reporting_to.full_name if prof and prof.reporting_to else '',
            'joined_on':      prof.joined_on.strftime('%d %b %Y') if prof and prof.joined_on else '',
            'designation':    prof.designation if prof else '',
            'photo_base64':   None,
            'photo_type':     None,
        }

        # ── Fetch photo document if uploaded ──────────────────────────────
        if prof:
            photo_doc = EmployeeDocumentMaster.objects.filter(
                employee_professional_details=prof,
                document_type='photo',
                deleted=False,
            ).order_by('-created_at').first()

            if photo_doc and photo_doc.file_path:
                try:
                    # file_path is stored as a full URL — fetch it and base64 encode
                    resp = http_requests.get(photo_doc.file_path, timeout=5)
                    if resp.ok:
                        data['photo_base64'] = base64.b64encode(resp.content).decode('utf-8')
                        content_type = resp.headers.get('Content-Type', 'image/jpeg')
                        data['photo_type'] = content_type
                except Exception:
                    pass  # photo fetch failure shouldn't break the letter data

        return Response(data)