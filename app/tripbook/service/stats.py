# services/stats.py
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth

from ..models import TripBook, Holiday
import json
from urllib.request import urlopen
from datetime import datetime

def get_yearly_stats(user, year):
    trips = TripBook.objects.filter(
        user=user,
        date__year=year,
        destinationAddress__isnull=False
    ).select_related("destinationAddress")

    total_km = trips.aggregate(
        total=Sum("destinationAddress__kilometers")
    )["total"] or 0

    months = (
        trips
        .annotate(month=ExtractMonth("date"))
        .values("month")
        .annotate(
            trips_count=Count("id"),
            total_kilometers=Sum("destinationAddress__kilometers"),
        )
        .order_by("month")
    )

    return {
        "year": year,
        "total_kilometers": total_km,
        "months": list(months),
    }


def get_monthly_stats(user, year, month):
    trips = TripBook.objects.filter(
        user=user,
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

    return {
        "year": year,
        "month": month,
        "total_kilometers": total_km,
        "destinations": list(destinations_data),
    }

def fetch_and_save_holidays(year: int, land: str = "NW"):
    url = f"https://feiertage-api.de/api/?jahr={year}&nur_land={land}"

    with urlopen(url) as response:
        if response.status != 200:
            return False

        data = json.loads(response.read())

    holidays = []
    for name, values in data.items():
        date_str = values.get("datum")
        if not date_str:
            continue

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        holidays.append(Holiday(name=name, date=date_obj))

    Holiday.objects.bulk_create(holidays)
    return True

# def fetch_and_save_holidays(year: int, land: str = "NW"):
#     url = f"https://feiertage-api.de/api/?jahr={year}&nur_land={land}"
#     response = requests.get(url)
#
#     if response.status_code != 200:
#         return False
#
#     data = response.json()
#
#     holidays = []
#     for name, values in data.items():
#         date_str = values.get("datum")
#         if not date_str:
#             continue
#
#         date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#         holidays.append(Holiday(name=name, date=date_obj))
#
#     Holiday.objects.bulk_create(holidays)
#     return True