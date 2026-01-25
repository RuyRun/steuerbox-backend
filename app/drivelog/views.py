import calendar
from datetime import date, timedelta

from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CalendarDay, DrivingLog, Destination
from .serializers import CalendarDaySerializer, DrivingLogSerializer, DestinationSerializer
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
        # 🔒 Sicherheitscheck: darf nur der Owner des Tages bearbeiten
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
