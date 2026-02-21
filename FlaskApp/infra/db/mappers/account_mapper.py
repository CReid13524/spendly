from FlaskApp.domainmodel import Account, User
from FlaskApp.infra.db.orm import AccountORM


def account_orm_to_domain(
        tx: AccountORM,
        user: User
) -> Account:
    return Account(
        account_id=tx.id,
        account_name=tx.name,
        account_type=tx.type,
        formatted_account=tx.formatted_account,
        attributes=[a.attribute for a in tx.attributes],
        currency=tx.currency,
        current_balance=tx.current_balance,
        available_balance=tx.available_balance,
        status=tx.status,
        created=tx.created,
        credit_limit=tx.credit_limit,
        overdrawn=tx.overdrawn,
        provider_name=tx.provider_name,
        provider_logo=tx.provider_logo,
        user=user,
    )


def account_domain_to_orm(
        tx: Account,
) -> AccountORM:
    return AccountORM(
        id=tx.id,
        name=tx.name,
        type=tx.type,
        formatted_account=tx.formatted_account,
        currency=tx.currency,
        current_balance=tx.current_balance,
        available_balance=tx.available_balance,
        status=tx.status,
        created=tx.created,
        credit_limit=tx.credit_limit,
        overdrawn=tx.overdrawn,
        user_id=tx.user.id,
        provider_name=tx.provider_name,
        provider_logo=tx.provider_logo,
    )
