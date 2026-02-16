from sqlalchemy.orm import Session

from FlaskApp.domainmodel import AkahuTransaction, Transaction, User
from FlaskApp.infra.db.mappers import akahu_transaction_orm_to_domain, akahu_transaction_domain_to_orm, \
    transaction_orm_to_domain, user_orm_to_domain
from FlaskApp.infra.db.orm import AkahuTransactionORM


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
