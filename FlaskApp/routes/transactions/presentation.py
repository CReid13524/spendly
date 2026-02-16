from FlaskApp.domainmodel import Transaction, Upload


def transaction_domain_to_json(transaction: Transaction) -> dict:
    return {
        "id": str(transaction.id),
        "amount": str(transaction.amount),
        "date": transaction.date.isoformat(),
        "description": transaction.description,
        "balance": str(transaction.balance),
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


def upload_domain_to_json(upload: Upload) -> dict:
    return {
        "id": str(upload.id),
        "filename": upload.file_name,
        "bank": upload.bank,
        "created": upload.created.isoformat(),
        "transaction_count": len(upload.transaction_ids)
    }
