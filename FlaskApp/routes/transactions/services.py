import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd
from werkzeug.datastructures import FileStorage

from FlaskApp.domainmodel import Transaction, Upload, User
from FlaskApp.infra.exceptions import AppError
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork
from FlaskApp.routes.transactions.assemblers import upload_csv_anz, upload_csv_kiwibank


def get_transactions(uow: AbstractUnitOfWork, user: User, **filters):
    with uow:
        transactions = uow.transactions.get_with_filters(user=user, **filters)
        return transactions


def create_transaction(uow: AbstractUnitOfWork, user: User, amount: Decimal, date: str, description: str | None,
                       balance: float | None, pending: bool | None, type: str | None, latitude: float | None,
                       longitude: float | None, category_id: str | None, account_id: str, merchant_id: str | None):
    with uow:
        account = uow.accounts.get(account_id, user=user)
        if account is None:
            raise Exception("Account not found")
        category = uow.categories.get(category_id, user=user) if category_id else None
        merchant = uow.merchants.get(merchant_id, user=user) if merchant_id else None
        transaction = Transaction(
            transaction_id=uuid.uuid4(),
            amount=amount,
            date=datetime.fromisoformat(date),
            description=description,
            balance=balance,
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


def update_transaction(uow: AbstractUnitOfWork, user: User, id: str, amount: Decimal, date: str,
                       description: str | None, balance: float | None, pending: bool, type: str | None, status: str,
                       latitude: float | None, longitude: float | None, category_id: str | None, account_id: str,
                       merchant_id: str | None, created: str):
    with uow:
        exists = uow.transactions.exists(id, user=user)
        if not exists:
            raise Exception("Transaction not found")
        account = uow.accounts.get(account_id, user=user)
        if account is None:
            raise Exception("Account not found")
        category = uow.categories.get(category_id, user=user) if category_id else None
        merchant = uow.merchants.get(merchant_id, user=user) if merchant_id else None

        transaction = Transaction(
            transaction_id=uuid.UUID(id),
            amount=amount,
            date=datetime.fromisoformat(date),
            description=description,
            balance=balance,
            pending=pending,
            transaction_type=type,
            status=status,
            created=datetime.fromisoformat(created),
            latitude=latitude,
            longitude=longitude,
            category=category,
            account=account,
            merchant=merchant,
            user=user
        )

        uow.transactions.add_or_update(transaction, user=user)


def delete_transaction(uow: AbstractUnitOfWork, user: User, transaction_id: str):
    with uow:
        exists = uow.transactions.exists(transaction_id, user=user)
        if not exists:
            raise Exception("Transaction not found")
        uow.transactions.delete(transaction_id, user=user)


def patch_transaction(uow: AbstractUnitOfWork, user: User, id: str, category_id: str | None = None,
                      account_id: str | None = None, merchant_id: str | None = None):
    with uow:
        # Get existing transaction, service will update as only updating relationships
        transaction = uow.transactions.get(id, user=user)
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


def get_uploads(uow: AbstractUnitOfWork, user: User):
    with uow:
        uploads = uow.uploads.list_uploads(user=user)
        return uploads


def upload_csv(uow: AbstractUnitOfWork, user: User, file: FileStorage, bank: str, account_id: str):
    df = pd.read_csv(file)

    bank_parsers = {
        "anz": upload_csv_anz,
        "kiwibank": upload_csv_kiwibank,
    }
    parser = bank_parsers.get(bank)

    try:
        df = parser(df)
    except KeyError:
        raise AppError(f"Unexpected CSV format. Suggested fix: Check selected bank ({bank})")

    with uow:
        account = uow.accounts.get(account_id, user=user)
        if account is None:
            raise Exception("Account not found")

        upload = Upload(
            upload_id=uuid.uuid4(),
            file_name=file.filename,
            user=user,
            transaction_ids=[],
            status='pending',
            bank=bank,
            created=datetime.now(tz=timezone.utc)
        )

        for _, row in df.iterrows():
            # TODO: Add category and merchant matching logic
            transaction_id = uuid.uuid4()
            upload.add_transaction(transaction_id)

            transaction = Transaction(
                transaction_id=transaction_id,
                amount=row['amount'],
                date=datetime.fromisoformat(row['date']),
                description=row['description'],
                transaction_type=row['type'],
                status='active',
                balance=row['balance'] if 'balance' in row else None,
                pending=False,
                # Currently, no supported banks have pending transactions in their CSV exports, so default to False. Can add support later if needed.
                created=datetime.now(tz=timezone.utc),
                latitude=None,
                longitude=None,
                category=None,
                account=account,
                merchant=None,
                user=user,
            )

            uow.transactions.add(transaction)

        uow.uploads.add(upload)


def delete_upload(uow: AbstractUnitOfWork, user: User, upload_id: str):
    with uow:
        exists = uow.uploads.exists(upload_id, user=user)
        if not exists:
            raise Exception("Upload not found")
        uow.uploads.delete(upload_id, user=user)


def update_transaction_locations(uow: AbstractUnitOfWork, user: User, transaction_id: str, latitude: float,
                                 longitude: float):
    with uow:
        transaction = uow.transactions.get(transaction_id, user=user)
        if transaction is None:
            raise Exception("Transaction not found")
        transaction.latitude = latitude
        transaction.longitude = longitude
        uow.transactions.add_or_update(transaction, user=user)
