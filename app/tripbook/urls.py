from django.urls import path, include
from rest_framework import routers

from .views import TripBookViewSet, DestinationAddressViewSet, CustomTripBookViewSet, MonthlyStatsView, YearlyStatsView, \
    YearlyReportPdfView, HolidayViewSet, CustomHolidayViewSet

router = routers.DefaultRouter()
router.register(r'destinationAddress', DestinationAddressViewSet, basename='destinationAddress')
router.register(r'tripBook', TripBookViewSet, basename='tripBook')

urlpatterns = [
    path('tripBook/calendar', CustomTripBookViewSet.as_view(), name='tripBook'),
    path('tripBook/stats/month', MonthlyStatsView.as_view(), name='tripBook-stats-month'),
    path('tripBook/stats/year', YearlyStatsView.as_view(), name='tripBook-stats-year'),
    path('tripBook/stats/createPdf', YearlyReportPdfView.as_view(), name='tripBook-create-pdf'),
    path('holiday', CustomHolidayViewSet.as_view(), name='tripBook-create-pdf'),
    path('', include(router.urls)),
]