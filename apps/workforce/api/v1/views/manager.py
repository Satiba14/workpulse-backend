from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.workforce.models import ManagerDetails
from apps.workforce.serializers.employee import ManagerDetailsSerializer


class ManagerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        managers = ManagerDetails.objects.filter(is_active=True)
        serializer = ManagerDetailsSerializer(managers, many=True)
        return Response(serializer.data)


class DepartmentManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dept_pk):
        try:
            manager = ManagerDetails.objects.get(
                department_id=dept_pk,
                is_active=True
            )

            serializer = ManagerDetailsSerializer(manager)
            return Response(serializer.data)

        except ManagerDetails.DoesNotExist:
            return Response({"manager": None})