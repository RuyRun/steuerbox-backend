from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import InvoiceReceipt, OutgoingInvoices

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "rg_date",
            "rg_number",
            "total",
            "company",
        ]


class InvoiceReceiptSerializer(ReceiptSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta(ReceiptSerializer.Meta):
        model = InvoiceReceipt
        fields = ReceiptSerializer.Meta.fields + [
            "user",
            "category",
        ]

class OutgoingInvoicesSerializer(ReceiptSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta(ReceiptSerializer.Meta):
        model = OutgoingInvoices
        fields = ReceiptSerializer.Meta.fields + [
            "user",
            "due_date",
            "paid_on",
        ]

class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="CSV-File", allow_empty_file=False)

class ErrorDetailSerializer(serializers.Serializer):
    row = serializers.IntegerField(help_text="Row number where the error occurred.")
    error = serializers.CharField(help_text="User-friendly error message.")
    rg_number = serializers.CharField(help_text="Invoice number for the failed record.")

class ImportResultSerializer(serializers.Serializer):
    imported = serializers.IntegerField(help_text="The number of successfully imported records.")
    failed = serializers.IntegerField(help_text="The number of failed records.")
    errors = ErrorDetailSerializer(many=True, help_text="A list of errors for the failed records.")

