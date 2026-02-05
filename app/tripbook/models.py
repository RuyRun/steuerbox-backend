from django.conf import settings
from django.db import models

class DestinationAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="destinationsAddress"
    )
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    kilometers = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.postal_code} {self.city}"

    class Meta:
        verbose_name = "DestinationAddress"
        verbose_name_plural = "DestinationAddresses"

class TripBook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tripBook"
    )
    date = models.DateField()
    destinationAddress = models.ForeignKey(DestinationAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip on {self.date}"

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"