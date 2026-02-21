from FlaskApp.domainmodel import AkahuAccount, Account
from FlaskApp.infra.presentation import format_cents
from FlaskApp.routes.accounts.presentation import account_domain_to_json

def akahu_account_domain_to_json(
        akahu_account: AkahuAccount
):
    return {
        "id": akahu_account.id,
        "authorisation": akahu_account.authorisation,
        "meta": akahu_account.meta,
        "connection_id": akahu_account.connection_id,
        "connection_type": akahu_account.connection_type,
        "refreshed": {k: v.isoformat() for k, v in akahu_account.refreshed.items()},
        "refresh_attempt": akahu_account.refresh_attempt.isoformat(),

        # Similar field to accounts
        "name": akahu_account.name,
        "type": akahu_account.type,
        "formatted_account": akahu_account.formatted_account,
        "attributes": akahu_account.attributes,
        "currency": akahu_account.currency,
        "current_balance": format_cents(akahu_account.current_balance), # Stored as dollars
        "available_balance": format_cents(akahu_account.available_balance) if akahu_account.available_balance is not None else None,
        "status": akahu_account.status,
        "created": akahu_account.created.isoformat(),
        "credit_limit": format_cents(akahu_account.credit_limit) if akahu_account.credit_limit is not None else None,
        "overdrawn": akahu_account.overdrawn,
        "connection_name": akahu_account.connection_name,
        "connection_logo": akahu_account.connection_logo,
    }

def compare_akahu_account_domain_to_json(
    akahu_account: AkahuAccount,
    account: Account
):
    return {
        'akahu_account': akahu_account_domain_to_json(akahu_account),
        'spendly_account': account_domain_to_json(account)
    }