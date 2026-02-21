from datetime import datetime, timezone
import uuid

import requests

from FlaskApp.domainmodel import Account, ExternalIdentity, User, AkahuTransaction, Transaction,AkahuAccount
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork
from FlaskApp.routes.akahu.assemblers import akahu_pending_transaction_to_domain, akahu_transaction_to_domain, akahu_account_to_domain, \
    akahu_merchant_to_domain, akahu_category_to_domain
from FlaskApp.infra.exceptions import ValidationError


def connect_akahu(
        bearer_token: str,
        app_id: str,
        uow: AbstractUnitOfWork,
        user: User
):
    with uow:
        akahu_identity = user.external_identities.get("akahu")

        if akahu_identity:
            raise ValidationError("Akahu identity already exists for user")

        client = AkahuClient(
            bearer_token=bearer_token,
            app_id=app_id
        )

        # Test credentials by fetching user info
        data = client.get_me()

        # Save the Akahu credentials as an external identity
        akahu_identity = ExternalIdentity(
            provider="akahu",
            external_id=data["_id"],
            email=data["email"],
            name=None,
            avatar_url=None,
            meta={
                "bearer_token": bearer_token,
                "app_id": app_id,
                "access_granted_at": data["access_granted_at"]
            },
            connected_at=datetime.now(tz=timezone.utc)
        )
        uow.users.add_external_identity(akahu_identity, user.id)


def sync_akahu(
        uow: AbstractUnitOfWork,
        full_sync: bool,
        user: User
):
    akahu_identity = user.external_identities.get("akahu")

    if not akahu_identity:
        raise Exception("No Akahu identity found for user")

    bearer_token = akahu_identity.meta.get('bearer_token', None)
    app_id = akahu_identity.meta.get('app_id', None)

    if not bearer_token or not app_id:
        raise Exception("Akahu credentials not found for user")

    client = AkahuClient(
        bearer_token=bearer_token,
        app_id=app_id
    )

    akahu_accounts = client.get_accounts()
    akahu_transactions = client.get_transactions(full_sync=full_sync)
    akahu_pending_transactions = client.get_pending_transactions()

    with uow:
        # Accounts
        accounts_for_balancing: list[uuid.UUID] = []
        for acc in akahu_accounts:
            uow.akahu_accounts.log_refresh_attempt(acc['_id'], user=user)  # Not included in update function

            # Source exisitng account ID
            existing_akahu_account: AkahuAccount | None = uow.akahu_accounts.get(acc['_id'], user=user)

            account, akahu_account = akahu_account_to_domain(acc, user=user,
                                                             existing_akahu_account=existing_akahu_account)

            # Must be done after transactions. Akahu balance = sum of transactions + Missing transactions (Akahu holds only 1 year before sign-up)
            if not existing_akahu_account:
                accounts_for_balancing.append(akahu_account.id)

            uow.accounts.add_or_update(account, user=user)
            uow.akahu_accounts.add_or_update(akahu_account, user=user)

        # Transactions
        for tx in akahu_transactions:
            akahu_account = uow.akahu_accounts.get(tx['_account'], user=user)
            if not akahu_account:
                raise Exception(f"Akahu Account not found")
            account = akahu_account.account

            # Merchant
            akahu_merchant = None
            if 'merchant' in tx:
                akahu_merchant = akahu_merchant_to_domain(tx)
                uow.akahu_merchants.add_or_update(akahu_merchant)

            # TODO: Merchant mapper function
            merchant = None

            # Category
            # TODO: ADD akahu category suggestion for auto mapping or solely own system?
            akahu_category = None
            if 'category' in tx:
                akahu_category = akahu_category_to_domain(tx['category'])
                uow.akahu_categories.add_or_update(akahu_category)

            # TODO: Category mapper function
            category = None

            # Source existing transaction by Akahu transaction ID
            existing_transaction: AkahuTransaction | None = uow.akahu_transactions.get(tx['_id'], user=user)

            # Transaction
            transaction, akahu_transaction = akahu_transaction_to_domain(
                akahu_tx=tx,
                existing_akahu_transaction=existing_transaction,
                user=user,
                account=account,
                akahu_account=akahu_account,
                category=category,
                akahu_category=akahu_category,
                merchant=merchant,
                akahu_merchant=akahu_merchant,
            )

            uow.transactions.add_or_update(transaction, user=user)
            uow.akahu_transactions.add_or_update(akahu_transaction, user=user)

        # Remove all pending transactions that are not user enforced
        # Hard delete since this data is considered volatile, with no definitve 'already imported' state, cannot be updated
        uow.akahu_transactions.delete_all_pending_transactions(user=user)

        # Pending Transactions
        for tx in akahu_pending_transactions:
            akahu_account = uow.akahu_accounts.get(tx['_account'], user=user)
            if not akahu_account:
                raise Exception(f"Akahu Account not found")
            account = akahu_account.account

            # Transaction
            transaction, akahu_transaction = akahu_pending_transaction_to_domain(
                akahu_tx=tx,
                user=user,
                account=account,
                akahu_account=akahu_account,
            )

            uow.transactions.add(transaction)
            uow.akahu_transactions.add(akahu_transaction)

        for account_id in accounts_for_balancing:
            balance_akahu_account(uow=uow, akahu_account_id=account_id, user=user)


def balance_akahu_account(uow: AbstractUnitOfWork, akahu_account_id: str, user: User):
    akahu_account = uow.akahu_accounts.get(akahu_account_id, user=user)
    account = akahu_account.account

    # Rebalance account balance based on sum of transactions
    balancing_amount = akahu_account.current_balance - account.current_balance
    balancing_transaction = Transaction(
        transaction_id=uuid.uuid4(),
        amount=balancing_amount, # Convert back to cents for transaction amount
        date=datetime.now(tz=timezone.utc),
        description="SYSTEM BALANCE ADJUSTMENT",
        balance=None,
        pending=False,
        transaction_type=None,
        status='hidden_active',
        created=datetime.now(tz=timezone.utc),
        latitude=None,
        longitude=None,
        category=None,
        account=account,
        merchant=None,
        user=user
    )
    uow.transactions.add(balancing_transaction)


class AkahuClient:
    def __init__(self, bearer_token: str, app_id: str):
        self.__bearer_token = bearer_token
        self.__app_id = app_id
        self.base_url = "https://api.akahu.io/v1"

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.__bearer_token}",
            "X-Akahu-ID": self.__app_id
        }

    def get_accounts(self):
        headers = self._get_headers()
        response = requests.get(
            f"{self.base_url}/accounts",
            headers=headers
        )
        data = response.json()

        if not response.ok:
            raise Exception(f"Error fetching accounts: {data.get('message', 'Unknown error')}")

        return data.get("items")

    def get_transactions(self, full_sync: bool = False):
        headers = self._get_headers()

        transactions = []
        cursor = None

        while True:

            response = requests.get(
                f"{self.base_url}/transactions",
                headers=headers,
                params={
                    "cursor": cursor,
                }
            )
            data = response.json()

            if not response.ok:
                raise Exception(f"Error fetching transactions: {data.get('message', 'Unknown error')}")

            new_transactions = data.get("items", [])
            transactions.extend(new_transactions)
            cursor = data["cursor"]["next"]
            if not full_sync or len(new_transactions) == 0 or cursor is None:
                # If not full sync, only fetch the first page (latest 50 transactions)
                break
        return transactions

    def get_pending_transactions(self):
        headers = self._get_headers()

        response = requests.get(
            f"{self.base_url}/transactions/pending",
            headers=headers
        )
        data = response.json()

        if not response.ok:
            raise Exception(f"Error fetching pending transactions: {data.get('message', 'Unknown error')}")

        return data.get("items")

    def get_me(self):
        headers = self._get_headers()

        response = requests.get(
            f"{self.base_url}/me",
            headers=headers
        )
        data = response.json()

        if not response.ok:
            raise ValidationError(f"Invalid Akahu credentials ({data.get('message', 'Unknown error')})")

        return data.get("item")

def get_akahu_accounts(
        uow: AbstractUnitOfWork,
        user: User,
        compare: bool
):
    with uow:
        akahu_accounts = uow.akahu_accounts.list_akahu_accounts(user=user)
        response = {akahu_account: akahu_account.account for akahu_account in akahu_accounts} if compare else akahu_accounts
        return response