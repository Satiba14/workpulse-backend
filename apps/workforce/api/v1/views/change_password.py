
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not request.user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect"},
                status=400
            )

        request.user.set_password(new_password)
        request.user.save()

        return Response({
            "message": "Password updated successfully"
        })