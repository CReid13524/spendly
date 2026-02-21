from decimal import Decimal


def format_cents(cents: Decimal) -> str:
    dollars = cents / 100
    if dollars == 0:
        return "0.00"
    return f"{dollars:.2f}"