from django import template

register = template.Library()

MONTHS = {
    1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
    5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
}

@register.filter
def month_name(month_number):
    return MONTHS.get(int(month_number), '')


@register.filter
def de_format(value):
    try:
        return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return value