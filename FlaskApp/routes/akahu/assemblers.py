import uuid
from datetime import datetime, timezone

from FlaskApp.domainmodel import Transaction, AkahuTransaction, User, AkahuAccount, AkahuCategory, AkahuMerchant, \
    Merchant, Category, Account


def akahu_transaction_to_domain(
        akahu_tx,
        *,
        existing_transaction: Transaction | None = None,
        is_pending: bool,
        user: User,
        account: Account,
        akahu_account: AkahuAccount,
        category: Category | None = None,
        akahu_category: AkahuCategory | None = None,
        merchant: Merchant | None = None,
        akahu_merchant: AkahuMerchant | None = None,
) -> tuple[Transaction, AkahuTransaction]:
    # Let repository handle updating exsiting transaction. Here just create a new object
    transaction = Transaction(
        transaction_id=existing_transaction.id if existing_transaction else uuid.uuid4(),
        amount=akahu_tx['amount'],
        date=datetime.fromisoformat(akahu_tx['date']),
        description=akahu_tx['description'],
        balance=akahu_tx['balance'],
        pending=is_pending,
        created=datetime.fromisoformat(akahu_tx['created_at']),
        latitude=None,
        longitude=None,
        user=user,
        account=account,
        category=category,
        merchant=merchant,
    )

    akahu_transaction = AkahuTransaction(
        akahu_transaction_id=akahu_tx['_id'],
        created=datetime.fromisoformat(akahu_tx['created_at']),
        updated=datetime.fromisoformat(akahu_tx['updated_at']),
        meta=akahu_tx['meta'],
        user=user,
        transaction=transaction,
        akahu_account=akahu_account,
        akahu_category=akahu_category,
        akahu_merchant=akahu_merchant
    )

    return transaction, akahu_transaction


def akahu_account_to_domain(
        akahu_account,
        *,
        existing_account: Account | None = None,
        user: User,
) -> tuple[Account, AkahuAccount]:
    # Let repository handle updating exsiting account. Here just create a new object
    account = Account(
        account_id=existing_account.id if existing_account else uuid.uuid4(),
        account_name=akahu_account['name'],
        account_type=akahu_account['type'],
        formatted_account=akahu_account['formatted_account'],
        attributes=akahu_account['attributes'],
        currency=akahu_account['balance']['currency'],
        current_balance=akahu_account['balance']['current'],
        available_balance=akahu_account['balance']['available'],
        status=akahu_account['status'],
        created=datetime.now(tz=timezone.utc),
        # Akahu doesn't provide a created timestamp for accounts, so we use the current time
        credit_limit=akahu_account['balance']['limit'],
        overdrawn=akahu_account['balance']['overdrawn'],
        user=user,
    )

    akahu_account = AkahuAccount(
        akahu_account_id=akahu_account['_id'],
        authorisation=akahu_account['_authorisation'],
        meta=akahu_account['meta'],
        connection_id=akahu_account['connection']['_id'],
        connection_name=akahu_account['connection']['name'],
        connection_logo=akahu_account['connection']['logo'],
        connection_type=akahu_account['connection']['connection_type'],
        refreshed=akahu_account['refreshed'],
        refresh_attempt=datetime.now(tz=timezone.utc),  # Our refresh attempt
        user=user,
        account=account,
    )

    return account, akahu_account


def akahu_merchant_to_domain(
        tx,
        *,
        merchant: Merchant | None = None,
) -> AkahuMerchant:
    akahu_merchant = tx['merchant']
    return AkahuMerchant(
        akahu_merchant_id=akahu_merchant['_id'],
        nzbn=akahu_merchant['nzbn'] if 'nzbn' in akahu_merchant else None,
        name=akahu_merchant['name'],
        website=akahu_merchant['website'] if 'website' in akahu_merchant else None,
        logo=tx['meta']['logo'] if 'meta' in tx and 'logo' in tx['meta'] else None
    )


def akahu_category_to_domain(
        akahu_category
) -> AkahuCategory:
    return AkahuCategory(
        nzfcc_id=akahu_category['_id'],
        nzfcc_name=akahu_category['name'],
        groups=akahu_category['groups'],
    )
