from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.workforce.serializers.profile import ProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = ProfileSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)
    def put(self, request):
        serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={'request': request}
)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)