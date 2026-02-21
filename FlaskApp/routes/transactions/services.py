import uuid
from datetime import datetime, timezone
from decimal import Decimal

from FlaskApp.domainmodel import Transaction, User
from FlaskApp.infra.services import to_amount_cents
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork


def get_transactions(uow: AbstractUnitOfWork, user: User, **filters):
    with uow:
        if filters.get('start_amount'):
            filters['start_amount'] = to_amount_cents(filters['start_amount'])
        if filters.get('end_amount'):
            filters['end_amount'] = to_amount_cents(filters['end_amount'])
        transactions = uow.transactions.get_with_filters(user=user, **filters)
        return transactions


def create_transaction(uow: AbstractUnitOfWork, user: User, amount: str, date: str, description: str | None,
                       balance: str | None, pending: bool | None, type: str | None, latitude: float | None,
                       longitude: float | None, category_id: str | None, account_id: str, merchant_id: str | None):
    with uow:
        account = uow.accounts.get(account_id, user=user)
        if account is None:
            raise Exception("Account not found")
        category = uow.categories.get(category_id, user=user) if category_id else None
        merchant = uow.merchants.get(merchant_id, user=user) if merchant_id else None
        transaction = Transaction(
            transaction_id=uuid.uuid4(),
            amount=to_amount_cents(amount),
            date=datetime.fromisoformat(date),
            description=description,
            balance=to_amount_cents(balance) if balance is not None else None,
            pending=pending,
            transaction_type=type,
            status='active',
            created=datetime.now(tz=timezone.utc),
            latitude=latitude,
            longitude=longitude,
            category=category,
            account=account,
            merchant=merchant,
            user=user
        )
        uow.transactions.add(transaction)


def update_transaction(uow: AbstractUnitOfWork, user: User, transaction_id: str, amount: str, date: str,
                       description: str | None, balance: str | None, pending: bool, type: str | None,
                       latitude: float | None, longitude: float | None, category_id: str | None, account_id: str,
                       merchant_id: str | None):
    with uow:
        transaction = uow.transactions.get(transaction_id, user=user)
        if transaction is None:
            raise Exception("Transaction not found")
        account = uow.accounts.get(account_id, user=user)
        if account is None:
            raise Exception("Account not found")
        category = uow.categories.get(category_id, user=user) if category_id else None
        merchant = uow.merchants.get(merchant_id, user=user) if merchant_id else None

        transaction.amount=to_amount_cents(amount)
        transaction.date=datetime.fromisoformat(date)
        transaction.description=description
        transaction.balance=to_amount_cents(balance) if balance is not None else None
        transaction.pending=pending
        transaction.type=type
        transaction.latitude=latitude
        transaction.longitude=longitude
        transaction.category=category
        transaction.account=account
        transaction.merchant=merchant

        uow.transactions.add_or_update(transaction, user=user)


def delete_transaction(uow: AbstractUnitOfWork, user: User, transaction_id: str):
    with uow:
        exists = uow.transactions.exists(transaction_id, user=user)
        if not exists:
            raise Exception("Transaction not found")
        uow.transactions.delete(transaction_id, user=user)


def patch_transaction(uow: AbstractUnitOfWork, user: User, transaction_id: str, category_id: str | None = None,
                      account_id: str | None = None, merchant_id: str | None = None):
    with uow:
        # Get existing transaction, service will update as only updating relationships
        transaction = uow.transactions.get(transaction_id, user=user)
        if transaction is None:
            raise Exception("Transaction not found")

        account = None
        if account_id:
            account = uow.accounts.get(account_id, user=user)
            if account is None:
                raise Exception("Account not found")

        category = uow.categories.get(category_id, user=user) if category_id else None
        if category_id and category is None:
            raise Exception("Category not found")

        merchant = uow.merchants.get(merchant_id, user=user) if merchant_id else None
        if merchant_id and merchant is None:
            raise Exception("Merchant not found")

        transaction.account = account if account_id else transaction.account
        transaction.category = category if category_id else transaction.category
        transaction.merchant = merchant if merchant_id else transaction.merchant

        uow.transactions.add_or_update(transaction, user=user)

def update_transaction_locations(uow: AbstractUnitOfWork, user: User, transaction_id: str, latitude: float,
                                 longitude: float):
    with uow:
        transaction = uow.transactions.get(transaction_id, user=user)
        if transaction is None:
            raise Exception("Transaction not found")
        transaction.latitude = latitude
        transaction.longitude = longitude
        uow.transactions.add_or_update(transaction, user=user)
