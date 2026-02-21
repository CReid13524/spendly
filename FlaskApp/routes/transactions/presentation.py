from FlaskApp.domainmodel import Transaction
from FlaskApp.infra.presentation import format_cents


def transaction_domain_to_json(transaction: Transaction) -> dict:
    return {
        "id": str(transaction.id),
        "amount": format_cents(transaction.amount),  # Convert cents to dollars
        "date": transaction.date.isoformat(),
        "description": transaction.description,
        "balance": format_cents(transaction.balance) if transaction.balance is not None else None,
        "pending": transaction.pending,
        'type': transaction.type,
        'status': transaction.status,
        "created": transaction.created.isoformat(),
        "latitude": transaction.latitude,
        "longitude": transaction.longitude,
        "category_id": str(transaction.category.id) if transaction.category else None,
        "account_id": str(transaction.account.id),
        "merchant_id": str(transaction.merchant.id) if transaction.merchant else None
    }
