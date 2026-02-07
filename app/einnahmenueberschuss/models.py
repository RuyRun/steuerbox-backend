from django.conf import settings
from django.db import models

class Receipt(models.Model):
    rg_date = models.DateField(db_index=True)
    rg_number = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.CharField(max_length=255)

    class Meta:
        abstract = True


class InvoiceReceipt(Receipt):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoice_receipts"
    )
    category = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.rg_number} {self.company}"

    class Meta:
        verbose_name_plural = "Invoice Receipts"
        ordering = ["rg_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "rg_number"],
                name="unique_invoice_receipt_per_user"
            )
        ]


class OutgoingInvoices(Receipt):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="outgoing_receipts"
    )
    paid_on = models.DateField(null=True, blank=True)
    due_date = models.DateField(db_index=True)

    def __str__(self):
        return f"{self.rg_date} {self.company}"
    class Meta:
        verbose_name_plural = "Outgoing Invoices"
        ordering = ["rg_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "rg_number"],
                name="unique_outgoing_invoice_per_user"
            )
        ]
