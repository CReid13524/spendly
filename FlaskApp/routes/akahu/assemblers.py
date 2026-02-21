from decimal import ROUND_HALF_UP, Decimal
import uuid
from datetime import datetime, timezone

from FlaskApp.domainmodel import Transaction, AkahuTransaction, User, AkahuAccount, AkahuCategory, AkahuMerchant, \
    Merchant, Category, Account
from FlaskApp.infra.services import to_amount_cents


def akahu_transaction_to_domain(
        akahu_tx,
        *,
        existing_akahu_transaction: AkahuTransaction | None = None,
        user: User,
        account: Account,
        akahu_account: AkahuAccount,
        category: Category | None = None,
        akahu_category: AkahuCategory | None = None,
        merchant: Merchant | None = None,
        akahu_merchant: AkahuMerchant | None = None,
) -> tuple[Transaction, AkahuTransaction]:
    # Let repository handle updating exsiting transaction. Here just update all possible fields
    if existing_akahu_transaction:
        # Update non-overwritten fields on transaction. Observed as not overwritten if no difference is detected
        transaction = existing_akahu_transaction.transaction

        if existing_akahu_transaction.amount == transaction.amount:
            transaction.amount=to_amount_cents(akahu_tx['amount'])
        if existing_akahu_transaction.date == transaction.date:
            transaction.date=datetime.fromisoformat(akahu_tx['date'])
        if existing_akahu_transaction.description == transaction.description:
            transaction.description=akahu_tx['description']
        if existing_akahu_transaction.balance == transaction.balance:
            transaction.balance=to_amount_cents(akahu_tx['balance']) if akahu_tx['balance'] is not None else None
        if existing_akahu_transaction.type == transaction.type:
            transaction.type=akahu_tx['type'].lower()

        existing_akahu_transaction.created=datetime.fromisoformat(akahu_tx['created_at']) # Should not change but just in case
        existing_akahu_transaction.updated=datetime.fromisoformat(akahu_tx['updated_at'])
        existing_akahu_transaction.meta=akahu_tx['meta']
        existing_akahu_transaction.amount=to_amount_cents(akahu_tx['amount'])
        existing_akahu_transaction.date=datetime.fromisoformat(akahu_tx['date'])
        existing_akahu_transaction.description=akahu_tx['description']
        existing_akahu_transaction.balance=to_amount_cents(akahu_tx['balance']) if akahu_tx['balance'] is not None else None
        existing_akahu_transaction.type=akahu_tx['type'].lower()
        existing_akahu_transaction.akahu_merchant = akahu_merchant
        existing_akahu_transaction.akahu_category = akahu_category

        return transaction, existing_akahu_transaction

    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        amount=to_amount_cents(akahu_tx['amount']),
        date=datetime.fromisoformat(akahu_tx['date']),
        description=akahu_tx['description'],
        balance=to_amount_cents(akahu_tx['balance']) if akahu_tx['balance'] is not None else None,
        transaction_type=akahu_tx['type'].lower(),
        status='active',
        pending=False,
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

        amount=to_amount_cents(akahu_tx['amount']),
        date=datetime.fromisoformat(akahu_tx['date']),
        description=akahu_tx['description'],
        balance=to_amount_cents(akahu_tx['balance']) if akahu_tx['balance'] is not None else None,
        type=akahu_tx['type'],
        pending=False,

        user=user,
        transaction=transaction,
        akahu_account=akahu_account,
        akahu_category=akahu_category,
        akahu_merchant=akahu_merchant
    )

    return transaction, akahu_transaction

def akahu_pending_transaction_to_domain(
        akahu_tx,
        *,
        user: User,
        account: Account,
        akahu_account: AkahuAccount,
) -> tuple[Transaction, AkahuTransaction]:

    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        amount=to_amount_cents(akahu_tx['amount']),  # Convert dollars to cents
        date=datetime.fromisoformat(akahu_tx['date']),
        description=akahu_tx['description'],
        balance=None,
        transaction_type=akahu_tx['type'].lower(),
        status='active',
        pending=True,
        created=datetime.now(tz=timezone.utc),  # Our created timestamp since Akahu doesn't provide one for pending transactions
        latitude=None,
        longitude=None,
        user=user,
        account=account,
        category=None,
        merchant=None,
    )

    akahu_transaction = AkahuTransaction(
        akahu_transaction_id=f"pending-{uuid.uuid4().hex}",  # Pending transactions have a temporary ID to avoid conflicts with existing transactions
        created=datetime.now(tz=timezone.utc),  # Our created timestamp since Akahu doesn't provide one for pending transactions
        updated=datetime.fromisoformat(akahu_tx['updated_at']),
        meta={},
        amount=to_amount_cents(akahu_tx['amount']),
        date=datetime.fromisoformat(akahu_tx['date']),
        description=akahu_tx['description'],
        balance=None,
        type=akahu_tx['type'],
        pending=True,
        user=user,
        transaction=transaction,
        akahu_account=akahu_account,
        akahu_category=None,
        akahu_merchant=None
    )

    return transaction, akahu_transaction

def akahu_account_to_domain(
        akahu_account,
        *,
        existing_akahu_account: AkahuAccount | None,
        user: User,
) -> tuple[Account, AkahuAccount]:
    # Let repository handle updating exsiting account.
    if existing_akahu_account:
        account = existing_akahu_account.account

        # Update non-overwritten fields on account. Observed as not overwritten if no difference is detected
        if existing_akahu_account.name == account.name:
            account.name = akahu_account['name']
        if existing_akahu_account.type.lower() == account.type:
            account.type = akahu_account['type'].lower()
        if existing_akahu_account.formatted_account == account.formatted_account:
            account.formatted_account = akahu_account['formatted_account']
        if [x.lower() for x in existing_akahu_account.attributes] == account.attributes:
            account.attributes = [x.lower() for x in akahu_account['attributes']]
        if existing_akahu_account.currency == account.currency:
            account.currency = akahu_account['balance']['currency']
        if existing_akahu_account.credit_limit == account.credit_limit:
            account.credit_limit = to_amount_cents(akahu_account['balance']['limit']) if 'limit' in akahu_account['balance'] else None

        # Update all possible fields on existing akahu account
        existing_akahu_account.authorisation = akahu_account['_authorisation']
        existing_akahu_account.meta = akahu_account['meta']
        existing_akahu_account.connection_id = akahu_account['connection']['_id']
        existing_akahu_account.connection_type = akahu_account['connection']['connection_type']
        existing_akahu_account.refreshed = akahu_account['refreshed']
        existing_akahu_account.name = akahu_account['name']
        existing_akahu_account.type = akahu_account['type'].lower()
        existing_akahu_account.formatted_account = akahu_account['formatted_account']
        existing_akahu_account.attributes = akahu_account['attributes']
        existing_akahu_account.currency = akahu_account['balance']['currency']
        existing_akahu_account.current_balance = to_amount_cents(akahu_account['balance']['current'])
        existing_akahu_account.available_balance = to_amount_cents(akahu_account['balance']['available']) if 'available' in akahu_account['balance'] else None
        existing_akahu_account.status = 'active' if akahu_account['status'] == 'ACTIVE' else 'deleted'
        existing_akahu_account.credit_limit = to_amount_cents(akahu_account['balance']['limit']) if 'limit' in akahu_account['balance'] else None
        existing_akahu_account.overdrawn = akahu_account['balance']['overdrawn'] if 'overdrawn' in akahu_account['balance'] else None
        existing_akahu_account.connection_name = akahu_account['connection']['name']
        existing_akahu_account.connection_logo = akahu_account['connection']['logo']

        return account, existing_akahu_account

    # No existing account, create new account and akahu account
    account = Account(
        account_id=uuid.uuid4(),
        account_name=akahu_account['name'],
        account_type=akahu_account['type'].lower(),
        formatted_account=akahu_account['formatted_account'],
        attributes=[a.lower() for a in akahu_account['attributes']],
        currency=akahu_account['balance']['currency'],
        current_balance=0,  # We set this to 0 as it will be updated when transactions are added. (Only domain state, not persisted value)
        available_balance=0,  # We set this to 0 as it will be updated when transactions are added. (Only domain state, not persisted value)
        status='active' if akahu_account['status'] == 'ACTIVE' else 'deleted',
        created=datetime.now(tz=timezone.utc), # Akahu doesn't provide a created timestamp for accounts, so we use the current time
        provider_name=akahu_account['connection']['name'],
        provider_logo=akahu_account['connection']['logo'],
        credit_limit=to_amount_cents(akahu_account['balance']['limit']) if 'limit' in akahu_account['balance'] else None,
        overdrawn=akahu_account['balance']['overdrawn'] if 'overdrawn' in akahu_account['balance'] else None,
        user=user,
    )

    akahu_account = AkahuAccount(
        akahu_account_id=akahu_account['_id'],
        authorisation=akahu_account['_authorisation'],
        meta=akahu_account['meta'],
        connection_id=akahu_account['connection']['_id'],
        connection_type=akahu_account['connection']['connection_type'],
        refreshed={k: datetime.fromisoformat(v) for k, v in akahu_account['refreshed'].items()},
        refresh_attempt=datetime.now(tz=timezone.utc),  # Our refresh attempt

        account_name=akahu_account['name'],
        account_type=akahu_account['type'],
        formatted_account=akahu_account['formatted_account'],
        attributes=akahu_account['attributes'],
        currency=akahu_account['balance']['currency'],
        current_balance=to_amount_cents(akahu_account['balance']['current']),
        available_balance=to_amount_cents(akahu_account['balance']['available']) if 'available' in akahu_account['balance'] else None,
        status='active' if akahu_account['status'] == 'ACTIVE' else 'deleted',
        created=datetime.now(tz=timezone.utc), # Akahu doesn't provide a created timestamp for accounts, so we use the current time
        credit_limit=to_amount_cents(akahu_account['balance']['limit']) if 'limit' in akahu_account['balance'] else None,
        overdrawn=akahu_account['balance']['overdrawn'] if 'overdrawn' in akahu_account['balance'] else None,
        connection_name=akahu_account['connection']['name'],
        connection_logo=akahu_account['connection']['logo'],

        user=user,
        account=account,
    )

    return account, akahu_account


def akahu_merchant_to_domain(
        tx
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
