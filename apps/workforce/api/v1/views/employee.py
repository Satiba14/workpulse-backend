from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.workforce.serializers.employee import (
    EmployeeListSerializer, EmployeeDetailSerializer,
    EmployeeCreateSerializer
)
from apps.workforce.services import (
    get_all_employees, get_employee_by_id,
    create_employee, update_employee, delete_employee
)


class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        filters = {
            'search':     request.query_params.get('search', ''),
            'department': request.query_params.get('department', ''),
            'status':     request.query_params.get('status', ''),
        }
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        employees = get_all_employees(filters=filters)
        return Response(EmployeeListSerializer(employees, many=True).data)

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        emp = create_employee(
            data=serializer.validated_data,
            user=request.user,
            request=request
        )
        return Response(EmployeeDetailSerializer(emp).data, status=201)


class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        emp, error = get_employee_by_id(pk)
        if error:
            return Response(error, status=404)
        return Response(EmployeeDetailSerializer(emp).data)

    def put(self, request, pk):
        emp, error = get_employee_by_id(pk)
        if error:
            return Response(error, status=404)
        
        data = request.data

        emp = update_employee(
            emp=emp,
            data=data,
            user=request.user,
            request=request
        )
        return Response(EmployeeDetailSerializer(emp).data)

    def delete(self, request, pk):
        emp, error = get_employee_by_id(pk)
        if error:
            return Response(error, status=404)
        delete_employee(emp=emp, user=request.user, request=request)
        return Response(status=204)