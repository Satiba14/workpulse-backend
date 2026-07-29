from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.workforce.serializers.auth import LoginSerializer
from apps.workforce.services import login_user, logout_user

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        user, data = login_user(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response(data, status=401)
        return Response(data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        success, data = logout_user(
            request,
            refresh_token=request.data.get('refresh'),
            user=user
        )
        if not success:
            return Response(data, status=400)
        return Response(data)
    
    