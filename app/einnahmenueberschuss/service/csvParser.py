import csv
import logging
from datetime import datetime
from decimal import Decimal
from io import TextIOWrapper

from django.core.exceptions import ValidationError

from ..models import InvoiceReceipt, OutgoingInvoices

logger = logging.getLogger(__name__)  # Logger für diese Datei
logging.basicConfig(level=logging.INFO)  # Ausgabe auf der Konsole

def parse_decimal(value):
    if not value:
        return Decimal("0.00")
    try:
        return Decimal(value.replace(".", "").replace(",", "."))
    except Exception:
        raise ValueError(f"Ungültiger Betrag: {value}")

def parse_date(value):
    if not value:
        return None
    value = value.strip().replace('"', '')  # Anführungszeichen entfernen
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError(f"Ungültiges Datum: {value}")

def generate_error_message(e, row, row_number):
    """
    This function creates a user-friendly error message depending on the error type.
    """
    error_message = "Unknown error"

    if isinstance(e, ValueError):
        if "RG-Datum" in str(e):
            error_message = "The invoice date is invalid."
        elif "Gesamtbetrag" in str(e):
            error_message = "The amount is invalid."
        elif "Fällig" in str(e):
            error_message = "The due date is invalid."
        else:
            error_message = "An error was found in the data."
    elif isinstance(e, ValidationError):
        # Check if ValidationError contains messages, then extract the first message
        if e.messages:
            error_message = f"Validation error: {e.messages[0]}"  # Use the first message
        else:
            error_message = "Unknown validation error"

    logger.error(f"Error in row {row_number}: {e}\nRow-Content: {row}")

    return {
        "row": row_number,
        "error": error_message,
        "rg_number": row.get("RG-Nr."),
    }


def import_csv(file, user, import_type):
    decoded = TextIOWrapper(file, encoding="utf-8-sig", errors="replace")
    reader = csv.DictReader(decoded, delimiter=";")
    reader.fieldnames = [name.strip() for name in reader.fieldnames]

    objects = []
    errors = []

    for row_number, row in enumerate(reader, start=2):
        # Werte trimmen und Anführungszeichen entfernen
        row = {k.strip(): (v.strip().replace('"', '') if v else "") for k, v in row.items()}

        try:
            if import_type == "income":
                obj = InvoiceReceipt(
                    user=user,
                    rg_date=parse_date(row["RG-Datum"]),
                    rg_number=row["RG-Nr."],
                    total=parse_decimal(row["Gesamtbetrag"]),
                    company=row["Firmenname"],
                    category=row.get("Kategorie") or "unknown",
                )

            elif import_type == "outgoing":
                rg_date = parse_date(row.get("RG-Datum"))
                if not rg_date:
                    raise ValueError("RG-Datum fehlt oder ungültig")

                due_date = parse_date(row.get("Fällig"))
                paid_on = parse_date(row.get("bezahlt am"))

                obj = OutgoingInvoices(
                    user=user,
                    rg_date=rg_date,
                    rg_number=row.get("RG-Nr."),
                    total=parse_decimal(row.get("Gesamtbetrag")),
                    company=row.get("Firmenname"),
                    due_date=due_date,
                    paid_on=paid_on,
                )

            obj.full_clean()
            objects.append(obj)

        except (ValueError, ValidationError) as e:
            error = generate_error_message(e, row, row_number)
            errors.append(error)

    if objects:
        try:
            model = InvoiceReceipt if import_type == "income" else OutgoingInvoices
            model.objects.bulk_create(objects)
        except Exception as e:
            logger.error(f"Error at bulk_create: {e}")

    return {
        "imported": len(objects),
        "failed": len(errors),
        "errors": errors,
    }
