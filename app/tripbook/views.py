from collections import defaultdict
from datetime import date, timedelta
import calendar

from django.db.models.aggregates import Sum, Count
from django.db.models.functions import ExtractMonth
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import DestinationAddress, TripBook
from .serializers import DestinationAddressSerializer, TripBookSerializer, MonthlyStatsSerializer, YearlyStatsSerializer


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

        trips = TripBook.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month,
            destinationAddress__isnull=False
        ).select_related("destinationAddress")

        total_km = trips.aggregate(
            total=Sum("destinationAddress__kilometers")
        )["total"] or 0

        destinations_qs = trips.values(
            "destinationAddress__id",
            "destinationAddress__street",
            "destinationAddress__postal_code",
            "destinationAddress__city",
        ).annotate(
            trips_count=Count("id"),
            km_total=Sum("destinationAddress__kilometers"),
        ).order_by("-trips_count")

        destinations_data = [
            {
                "id": d["destinationAddress__id"],
                "street": d["destinationAddress__street"],
                "postal_code": d["destinationAddress__postal_code"],
                "city": d["destinationAddress__city"],
                "trips_count": d["trips_count"],
                "km_total": d["km_total"],
            }
            for d in destinations_qs
        ]

        serializer = MonthlyStatsSerializer({
            "year": int(year),
            "month": int(month),
            "total_kilometers": total_km,
            "destinations": destinations_data,
        })

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

        trips = TripBook.objects.filter(
            user=request.user,
            date__year=year,
            destinationAddress__isnull=False
        ).select_related("destinationAddress")

        total_km_year = trips.aggregate(
            total=Sum("destinationAddress__kilometers")
        )["total"] or 0

        months_qs = (
            trips
            .annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(
                trips_count=Count("id"),
                total_kilometers=Sum("destinationAddress__kilometers"),
            )
            .order_by("month")
        )

        months_data = list(months_qs)

        serializer = YearlyStatsSerializer({
            "year": int(year),
            "total_kilometers": total_km_year,
            "months": months_data,
        })

        return Response(serializer.data)