from django.conf import settings
from django.db import models


class Destination(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="destinations"
    )
    name = models.CharField(max_length=255)
    km = models.DecimalField(max_digits=7, decimal_places=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CalendarDay(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_days"
    )
    date = models.DateField()

    class Meta:
        unique_together = ("user", "date")
        ordering = ["date"]


class DrivingLog(models.Model):
    day = models.OneToOneField(
        CalendarDay,
        on_delete=models.CASCADE,
        related_name="driving_log"
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.PROTECT
    )
    notes = models.TextField(blank=True)
