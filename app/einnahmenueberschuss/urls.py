from django.urls import path

from .views import ReceiptCSVImportView

urlpatterns = [
    path(
        "upload/receipt",
        ReceiptCSVImportView.as_view(),
        name="upload-outgoing-csv",
    ),
]
