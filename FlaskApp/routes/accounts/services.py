import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd
from werkzeug.datastructures import FileStorage

from FlaskApp.domainmodel import Account, User, Upload, Transaction
from FlaskApp.infra.exceptions import AppError
from FlaskApp.infra.services import to_amount_cents
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork
from FlaskApp.routes.accounts.assemblers import upload_csv_anz, upload_csv_kiwibank

def create_account(uow: AbstractUnitOfWork, user: User, name: str, type: str, formatted_account: str, attributes: list, currency: str, credit_limit: str):
    with uow:
        account = Account(
            account_id=uuid.uuid4(),
            account_name=name,
            account_type=type,
            formatted_account=formatted_account,
            attributes=attributes,
            currency=currency,
            current_balance=0,  # We set this to 0 as it will be updated when transactions are added. (Only domain state, not persisted value)
            available_balance=0,  # We set this to 0 as it will be updated when transactions are added. (Only domain state, not persisted value)
            status='active',
            created=datetime.now(timezone.utc),
            credit_limit=to_amount_cents(credit_limit),
            provider_name='Spendly',  # We set this to Spendly as it's a user-created account. (Only domain state, not persisted value)
            provider_logo='about:blank', # TODO: Our logo
            overdrawn=False,  # We set this to False as it will be updated when transactions are added. (Only domain state, not persisted value)
            user=user
        )
        uow.accounts.add(account)

def get_accounts(uow: AbstractUnitOfWork, user: User):
    with uow:
        accounts = uow.accounts.get_all_for_user(user=user)
        return accounts

def update_account(uow: AbstractUnitOfWork, user: User, account_id: str, name: str, type: str, formatted_account: str, attributes: list, currency: str, credit_limit: str):
    with uow:
        account = uow.accounts.get(account_id=account_id, user=user)
        if not account:
            raise AppError("Account not found")
        account.name = name
        account.type = type
        account.formatted_account = formatted_account
        account.attributes = attributes
        account.currency = currency
        account.credit_limit = to_amount_cents(credit_limit)
        uow.accounts.add_or_update(account, user=user)

def delete_account(uow: AbstractUnitOfWork, user: User, account_id: str):
    with uow:
        account = uow.accounts.get(account_id=account_id, user=user)
        if not account:
            raise AppError("Account not found")
        uow.accounts.delete(account_id, user=user)

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
                amount=row['amount'], # Amount is already converted to cents in assembler
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

