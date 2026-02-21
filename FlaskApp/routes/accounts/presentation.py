

from FlaskApp.domainmodel import Account
from FlaskApp.domainmodel.upload import Upload
from FlaskApp.infra.presentation import format_cents


def account_domain_to_json(account: Account):
    return {
        'id': str(account.id),
        'name': account.name,
        'type': account.type,
        'formatted_account': account.formatted_account,
        'attributes': account.attributes,
        'currency': account.currency,
        'current_balance': format_cents(account.current_balance),
        'available_balance': format_cents(account.available_balance) if account.available_balance is not None else None,
        'status': account.status,
        'created': account.created.isoformat(),
        'credit_limit': format_cents(account.credit_limit) if account.credit_limit is not None else None,
        'overdrawn': account.overdrawn,
        'provider_name': account.provider_name,
        'provider_logo': account.provider_logo,
    }

def upload_domain_to_json(upload: Upload) -> dict:
    return {
        "id": str(upload.id),
        "filename": upload.file_name,
        "bank": upload.bank,
        "created": upload.created.isoformat(),
        "transaction_count": len(upload.transaction_ids)
    }
