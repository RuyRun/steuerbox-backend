from rest_framework import serializers
from .models import TripBook, DestinationAddress


class DestinationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationAddress
        fields = ['id', 'street', 'postal_code', 'city', 'kilometers']


class TripBookSerializer(serializers.ModelSerializer):
    destinationAddress = serializers.PrimaryKeyRelatedField(
        queryset=DestinationAddress.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = TripBook
        fields = ['id', 'date', 'destinationAddress', 'comment']


class DestinationMonthlyStatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    street = serializers.CharField()
    postal_code = serializers.CharField()
    city = serializers.CharField()
    trips_count = serializers.IntegerField()
    km_total = serializers.DecimalField(max_digits=10, decimal_places=2)

class MonthlyStatsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    total_kilometers = serializers.DecimalField(max_digits=10, decimal_places=2)
    destinations = DestinationMonthlyStatSerializer(many=True)

class MonthlySummarySerializer(serializers.Serializer):
    month = serializers.IntegerField()
    trips_count = serializers.IntegerField()
    total_kilometers = serializers.DecimalField(max_digits=10, decimal_places=2)

class YearlyStatsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    total_kilometers = serializers.DecimalField(max_digits=10, decimal_places=2)
    months = MonthlySummarySerializer(many=True)
