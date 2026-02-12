from datetime import datetime, timezone

import requests
from flask import g

from FlaskApp.domainmodel import Transaction, Account, ExternalIdentity
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork
from FlaskApp.routes.akahu.assemblers import akahu_transaction_to_domain, akahu_account_to_domain, \
    akahu_merchant_to_domain, akahu_category_to_domain


def connect_akahu(
        bearer_token: str,
        app_id: str,
        uow: AbstractUnitOfWork,
):
    with uow:
        akahu_identity = g.current_user.external_identities.get("akahu")

        if akahu_identity:
            raise ValueError("Akahu identity already exists for user")

        client = AkahuClient(
            bearer_token=bearer_token,
            app_id=app_id
        )

        # Test credentials by fetching user info
        try:
            data = client.get_me()
        except Exception as e:
            raise ValueError("Invalid Akahu credentials") from e

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
        uow.users.add_external_identity(akahu_identity, g.current_user.id)


def sync_akahu(
        uow: AbstractUnitOfWork,
        full_sync: bool,
):
    akahu_identity = g.current_user.external_identities.get("akahu")

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

    with uow:
        # Accounts
        for acc in akahu_accounts:
            uow.akahu_accounts.log_refresh_attempt(acc['_id'])  # Not included in update function

            # Source exisitng account ID
            existing_account: Account | None = uow.akahu_accounts.get_connected_account_by_id(acc['_id'])

            account, akahu_account = akahu_account_to_domain(acc, user=g.current_user,
                                                             existing_account=existing_account)
            uow.accounts.add_or_update(account)
            uow.akahu_accounts.add_or_update(akahu_account)

        # Transactions
        for tx in akahu_transactions:
            akahu_account = uow.akahu_accounts.get(tx['_account'])
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
            existing_transaction: Transaction | None = uow.akahu_transactions.get_connected_transaction_by_id(tx['_id'])

            # Transaction
            transaction, akahu_transaction = akahu_transaction_to_domain(
                akahu_tx=tx,
                is_pending=False,  # This endpointpoint does not consider pending transaction.
                existing_transaction=existing_transaction,
                user=g.current_user,
                account=account,
                akahu_account=akahu_account,
                category=category,
                akahu_category=akahu_category,
                merchant=merchant,
                akahu_merchant=akahu_merchant,
            )

            uow.transactions.add_or_update(transaction)
            uow.akahu_transactions.add_or_update(akahu_transaction)


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

        return data.get("items", [])

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
            print(f"Fetched {len(transactions)} transactions so far... Next cursor: {cursor}")
        return transactions

    def get_me(self):
        headers = self._get_headers()

        response = requests.get(
            f"{self.base_url}/me",
            headers=headers
        )
        data = response.json()

        if not response.ok:
            raise Exception(f"Error fetching user info: {data.get('message', 'Unknown error')}")

        return data.get("item")
