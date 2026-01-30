from rest_framework import serializers
from .models import CalendarDay, DrivingLog, Destination


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "is_active", "km"]
        read_only_fields = ["is_active"]



class DrivingLogSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(),
        source="destination",
        write_only=True
    )

    class Meta:
        model = DrivingLog
        fields = [
            "id",
            "day",
            "destination",
            "destination_id",
            "notes",
        ]

class CalendarDaySerializer(serializers.ModelSerializer):
    driving_log = DrivingLogSerializer(read_only=True)

    class Meta:
        model = CalendarDay
        fields = ["id","date", "driving_log"]

class DestinationStatSerializer(serializers.Serializer):
    name = serializers.CharField(source="destination__name")
    count = serializers.IntegerField()
    km_total = serializers.DecimalField(max_digits=10, decimal_places=1)


class MonthlyStatsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    total_km = serializers.DecimalField(max_digits=10, decimal_places=1)
    destinations = DestinationStatSerializer(many=True)

class MonthlyTotalSerializer(serializers.Serializer):
    month = serializers.DateField()
    total_km = serializers.DecimalField(max_digits=10, decimal_places=1)
    trips = serializers.IntegerField()


class YearlyStatsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    total_km = serializers.DecimalField(max_digits=10, decimal_places=1)
    monthly_totals = MonthlyTotalSerializer(many=True)
    destinations = DestinationStatSerializer(many=True)
