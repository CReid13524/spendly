from FlaskApp.domainmodel import Transaction, User

from FlaskApp.infra.db.mappers.account_mapper import account_orm_to_domain
from FlaskApp.infra.db.mappers.category_mapper import category_orm_to_domain
from FlaskApp.infra.db.mappers.merchant_mapper import merchant_orm_to_domain
from FlaskApp.infra.db.orm import TransactionORM


def transaction_orm_to_domain(
        tx: TransactionORM,
        user: User,
) -> Transaction:
    return Transaction(
        transaction_id=tx.id,
        amount=tx.amount,
        date=tx.date,
        description=tx.description,
        balance=tx.balance,
        pending=tx.pending,
        created=tx.created,
        latitude=tx.latitude,
        longitude=tx.longitude,

        user=user,
        account=account_orm_to_domain(tx.account, user=user),
        category=category_orm_to_domain(tx.category, user=user) if tx.category else None,
        merchant=merchant_orm_to_domain(tx.merchant, user=user) if tx.merchant else None,
    )


def transaction_domain_to_orm(
        tx: Transaction,
) -> TransactionORM:
    return TransactionORM(
        id=tx.id,
        amount=tx.amount,
        date=tx.date,
        description=tx.description,
        balance=tx.balance,
        pending=tx.pending,
        created=tx.created,
        latitude=tx.latitude,
        longitude=tx.longitude,

        user_id=tx.user.id,
        account_id=tx.account.id,
        category_id=tx.category.id if tx.category else None,
        merchant_id=tx.merchant.id if tx.merchant else None,
    )
