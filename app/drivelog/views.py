import calendar
from datetime import date, timedelta

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CalendarDay, DrivingLog, Destination
from .serializers import CalendarDaySerializer, DrivingLogSerializer, DestinationSerializer, MonthlyStatsSerializer, \
    YearlyStatsSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

class CalendarMonthView(APIView):
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
        responses=CalendarDaySerializer(many=True),
    )
    def get(self, request):
        year = int(request.query_params["year"])
        month = int(request.query_params["month"])

        first = date(year, month, 1)
        last = date(year, month, calendar.monthrange(year, month)[1])

        existing_days = CalendarDay.objects.filter(
            user=request.user,
            date__range=(first, last)
        )

        existing_dates = {d.date for d in existing_days}

        CalendarDay.objects.bulk_create([
            CalendarDay(user=request.user, date=first + timedelta(days=i))
            for i in range((last - first).days + 1)
            if (first + timedelta(days=i)) not in existing_dates
        ])

        days = CalendarDay.objects.filter(
            user=request.user,
            date__range=(first, last)
        ).select_related("driving_log__destination")

        serializer = CalendarDaySerializer(days, many=True)
        return Response(serializer.data)

class DrivingLogCreateView(CreateAPIView):
    serializer_class = DrivingLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class DrivingLogUpdateView(RetrieveUpdateAPIView):
    queryset = DrivingLog.objects.all()
    serializer_class = DrivingLogSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.day.user != self.request.user:
            raise PermissionDenied("Du darfst dieses Fahrtenbuch nicht bearbeiten.")
        return obj

class DestinationView(viewsets.ModelViewSet):
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Destination.objects.filter(user=self.request.user, is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MonthlyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MonthlyStatsSerializer,
        parameters=[
            OpenApiParameter("year", int),
            OpenApiParameter("month", int),
        ],
    )
    def get(self, request):
        year = int(request.query_params.get("year"))
        month = int(request.query_params.get("month"))

        logs = DrivingLog.objects.filter(
            day__user=request.user,
            day__date__year=year,
            day__date__month=month
        ).select_related("destination", "day")

        # 🔹 Gesamt-KM
        total_km = logs.aggregate(
            total=Sum("destination__km")
        )["total"] or 0

        # 🔹 Nutzung je Ziel
        destinations = logs.values(
            "destination__name"
        ).annotate(
            count=Count("id"),
            km_total=Sum("destination__km")
        ).order_by("-count")

        return Response({
            "year": year,
            "month": month,
            "total_km": total_km,
            "destinations": destinations
        })


class YearlyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=YearlyStatsSerializer,
        parameters=[OpenApiParameter("year", int)],
    )
    def get(self, request):
        year = int(request.query_params["year"])

        logs = DrivingLog.objects.filter(
            day__user=request.user,
            day__date__year=year
        )

        # 🔹 Gesamt-KM im Jahr
        total_km = logs.aggregate(
            total=Sum("destination__km")
        )["total"] or 0

        # 🔹 KM pro Monat
        months = logs.annotate(
            month=TruncMonth("day__date")
        ).values("month").annotate(
            total_km=Sum("destination__km"),
            trips=Count("id")
        ).order_by("month")

        # 🔹 Nutzung je Ziel
        destinations = logs.values("destination__name").annotate(
            count=Count("id"),
            km_total=Sum("destination__km")
        ).order_by("-km_total")

        data = {
            "year": year,
            "total_km": total_km,
            "monthly_totals": list(months),
            "destinations": list(destinations)
        }

        return Response(data)

