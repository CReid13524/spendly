from sqlalchemy.orm import Session

from FlaskApp.domainmodel import AkahuTransaction, Transaction, User
from FlaskApp.infra.db.mappers import akahu_transaction_orm_to_domain, akahu_transaction_domain_to_orm, \
    transaction_orm_to_domain, user_orm_to_domain
from FlaskApp.infra.db.orm import AkahuTransactionORM
from FlaskApp.infra.db.orm.transaction_orm import TransactionORM


class AkahuTransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, akahu_transaction: AkahuTransaction):
        orm = akahu_transaction_domain_to_orm(akahu_transaction)
        self.session.add(orm)

    def get(self, akahu_transaction_id: str, user: User) -> AkahuTransaction | None:
        orm = self.session.query(AkahuTransactionORM).filter_by(id=akahu_transaction_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return akahu_transaction_orm_to_domain(orm, user=user)

    def get_connected_transaction_by_id(self, akahu_transaction_id: str, user: User) -> Transaction | None:
        orm = self.session.query(AkahuTransactionORM).filter_by(id=akahu_transaction_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return transaction_orm_to_domain(orm.transaction, user=user)

    def add_or_update(self, akahu_transaction: AkahuTransaction, user: User):
        existing = self.session.query(AkahuTransactionORM).filter_by(id=akahu_transaction.id, user_id=user.id).first()
        if existing:
            # Update existing fields
            existing.updated = akahu_transaction.updated
            existing.meta = akahu_transaction.meta
            existing.akahu_category_id = akahu_transaction.akahu_category.id if akahu_transaction.akahu_category else None
            existing.akahu_merchant_id = akahu_transaction.akahu_merchant.id if akahu_transaction.akahu_merchant else None
        else:
            orm = akahu_transaction_domain_to_orm(akahu_transaction)
            self.session.add(orm)
    def list_pending_transactions(self, user: User) -> list[AkahuTransaction]:
        orms = self.session.query(AkahuTransactionORM).filter_by(pending=True, user_id=user.id).all()
        user = user_orm_to_domain(orms[0].user) if orms else None
        return [akahu_transaction_orm_to_domain(orm, user=user) for orm in orms]

    def delete_all_pending_transactions(self, user: User):
        # Find AkahuTransactionORMs with pending=True and related TransactionORM with pending=True
        from sqlalchemy import and_, select

        # Get transaction IDs to delete
        subquery = (
            self.session.query(AkahuTransactionORM.transaction_id)
            .join(TransactionORM, AkahuTransactionORM.transaction_id == TransactionORM.id)
            .filter(
                AkahuTransactionORM.pending == True,
                AkahuTransactionORM.user_id == user.id,
                TransactionORM.pending == True
            )
            .subquery()
        )
        # Delete from TransactionORM
        self.session.query(TransactionORM).filter(TransactionORM.id.in_(select(subquery))).delete(synchronize_session=False)
        # Delete from AkahuTransactionORM
        self.session.query(AkahuTransactionORM).filter(
            AkahuTransactionORM.pending == True,
            AkahuTransactionORM.user_id == user.id,
            AkahuTransactionORM.transaction_id.in_(select(subquery))
        ).delete(synchronize_session=False)
