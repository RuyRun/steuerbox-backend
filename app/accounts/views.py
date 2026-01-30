from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import MeSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MeSerializer,
        request=MeSerializer
    )
    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=MeSerializer,
        responses=MeSerializer
    )
    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)