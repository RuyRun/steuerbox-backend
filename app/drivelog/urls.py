from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CalendarMonthView, DrivingLogCreateView, DestinationView, DrivingLogUpdateView, MonthlyStatsView, YearlyStatsView

router = DefaultRouter()
router.register(r'destinations', DestinationView, basename='destination')

urlpatterns = [
    path("calendar/", CalendarMonthView.as_view()),
    path("driving-log/", DrivingLogCreateView.as_view()),
    path("driving-log/<int:pk>/", DrivingLogUpdateView.as_view()),
    path("stats/month/", MonthlyStatsView.as_view()),
    path("stats/year/", YearlyStatsView.as_view()),
    path("", include(router.urls)),

]
