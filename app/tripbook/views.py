from collections import defaultdict
from datetime import date, timedelta
import calendar

from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import render_to_string
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import DestinationAddress, TripBook
from .serializers import DestinationAddressSerializer, TripBookSerializer, MonthlyStatsSerializer, YearlyStatsSerializer
from .service.stats import get_yearly_stats, get_monthly_stats


class DestinationAddressViewSet(ModelViewSet):
    queryset = DestinationAddress.objects.all()
    serializer_class = DestinationAddressSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return DestinationAddress.objects.filter(user=self.request.user, is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TripBookViewSet(ModelViewSet):
    queryset = TripBook.objects.all()
    serializer_class = TripBookSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put', 'patch']

class CustomTripBookViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                description="Jahr des Kalenders",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="month",
                description="Monat des Kalenders",
                required=True,
                type=int,
            ),
        ],
        responses=TripBookSerializer(many=True),
    )
    def get(self, request):
        year = int(request.query_params["year"])
        month = int(request.query_params["month"])

        first = date(year, month, 1)
        last = date(year, month, calendar.monthrange(year, month)[1])

        existing_days = TripBook.objects.filter(
            user=request.user,
            date__range=(first, last)
        )

        existing_days = {d.date for d in existing_days}

        TripBook.objects.bulk_create([
            TripBook(user=request.user, date= first+ timedelta(days=i))
            for i in range((last-first).days + 1)
            if (first + timedelta(days=1)) not in existing_days
        ])

        days = TripBook.objects.filter(
            user=request.user,
            date__range=(first, last)
        ).select_related('destinationAddress').order_by('date')

        serializer = TripBookSerializer(days, many=True)
        return Response(serializer.data)


class MonthlyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MonthlyStatsSerializer,
        parameters=[
            OpenApiParameter("year", int, required=True),
            OpenApiParameter("month", int, required=True),
        ],
    )
    def get(self, request):
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        if not year or not month:
            return Response(
                {"detail": "year und month sind erforderlich"},
                status=400
            )

        serializer = MonthlyStatsSerializer(get_monthly_stats(user=request.user, year=year, month=month))

        return Response(serializer.data)

class YearlyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=YearlyStatsSerializer,
        parameters=[
            OpenApiParameter("year", int, required=True),
        ],
    )
    def get(self, request):
        year = request.query_params.get("year")

        if not year:
            return Response(
                {"detail": "year ist erforderlich"},
                status=400
            )

        serializer = YearlyStatsSerializer(get_yearly_stats(user=request.user, year=year))
        return Response(serializer.data)

class YearlyReportPdfView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("year", int, required=True),
        ],
    )
    def get(self, request):
        year = int(request.query_params.get("year"))

        yearly = get_yearly_stats(request.user, year)

        monthly = [
            get_monthly_stats(request.user, year, month)
            for month in range(1, 13)
        ]

        html = render_to_string(
            "reports/yearly_report.twig",
            {
                "yearly": yearly,
                "monthly": monthly,
                "user": request.user,
            }
        )

        pdf = HTML(string=html).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="report_{year}.pdf"'
        return response