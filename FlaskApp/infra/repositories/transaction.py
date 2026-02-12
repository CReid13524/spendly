from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Transaction
from FlaskApp.infra.db.mappers import transaction_orm_to_domain, transaction_domain_to_orm, user_orm_to_domain
from FlaskApp.infra.db.orm import TransactionORM


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, transaction: Transaction):
        orm = transaction_domain_to_orm(transaction)
        self.session.add(orm)

    def get(self, transaction_id: int) -> Transaction | None:
        orm = self.session.query(TransactionORM).filter_by(id=transaction_id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.account.user)
        return transaction_orm_to_domain(orm, user=user)

    def exists(self, transaction_id: int) -> bool:
        return self.session.query(TransactionORM).filter_by(id=transaction_id).first() is not None

    def add_or_update(self, transaction: Transaction):
        existing = self.session.query(TransactionORM).filter_by(id=transaction.id).first()
        if existing:
            # Update existing fields
            existing.amount = transaction.amount
            existing.date = transaction.date
            existing.description = transaction.description
            existing.account_id = transaction.account.id
            existing.category_id = transaction.category.id if transaction.category else None
            existing.merchant_id = transaction.merchant.id if transaction.merchant else None
        else:
            orm = transaction_domain_to_orm(transaction)
            self.session.add(orm)
