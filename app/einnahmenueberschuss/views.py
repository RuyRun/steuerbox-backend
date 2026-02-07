from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .serializers import CSVUploadSerializer, ImportResultSerializer, ErrorDetailSerializer
from .service.csvParser import import_csv


class ReceiptCSVImportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CSVUploadSerializer
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=CSVUploadSerializer,
        parameters=[
            OpenApiParameter(
                name="type",
                location=OpenApiParameter.QUERY,
                type=str,
                enum=["income", "outgoing"],
                required=True,
                description="Import-Typ: income oder outgoing"
            )
        ],
        responses={
            201: OpenApiResponse(
                description="CSV import successful",
                response=ImportResultSerializer  # Use the ImportResultSerializer here
            ),
            400: OpenApiResponse(
                description="Invalid CSV file or import type",
                response=ErrorDetailSerializer  # Return error details on failure
            )
        },
        description="CSV-Import für Income (InvoiceReceipt) oder OutgoingInvoices",
    )
    @action(detail=False, methods=['post'])
    def post(self, request, *args, **kwargs):
        import_type = request.query_params.get("type")
        if import_type not in ("income", "outgoing"):
            return Response(
                {"error": "type must  'income' or 'outgoing'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CSVUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = import_csv(
            file=serializer.validated_data["file"],
            user=request.user,
            import_type=import_type
        )

        return Response(result, status=status.HTTP_201_CREATED)
