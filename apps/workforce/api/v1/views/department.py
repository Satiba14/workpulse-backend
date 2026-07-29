from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.workforce.serializers.department import (
    DepartmentSerializer, DepartmentCreateSerializer
)
from apps.workforce.services import (
    get_all_departments, get_department_by_id,
    create_department, update_department, delete_department
)


class DepartmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        depts = get_all_departments().prefetch_related('employees')
        return Response(DepartmentSerializer(depts, many=True).data)

    def post(self, request):
        serializer = DepartmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            dept = create_department(
                data=serializer.validated_data,
                user=request.user,
                request=request
            )
            return Response(DepartmentSerializer(dept).data, status=201)
        return Response(serializer.errors, status=400)


class DepartmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        dept, error = get_department_by_id(pk)
        if error:
            return Response(error, status=404)
        return Response(DepartmentSerializer(dept).data)

    def put(self, request, pk):
        dept, error = get_department_by_id(pk)
        if error:
            return Response(error, status=404)
        dept = update_department(
            dept=dept,
            data=request.data,
            user=request.user,
            request=request
        )
        return Response(DepartmentSerializer(dept).data)

    def delete(self, request, pk):
        dept, error = get_department_by_id(pk)
        if error:
            return Response(error, status=404)
        delete_department(dept=dept, user=request.user, request=request)
        return Response(status=204)