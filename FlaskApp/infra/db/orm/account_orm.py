import uuid

from sqlalchemy import UUID, BigInteger, Column, DateTime, ForeignKey, Numeric, String, Boolean, and_, select, or_, func
from sqlalchemy.orm import relationship, column_property
from FlaskApp.infra.db.orm.transaction_orm import TransactionORM
from FlaskApp.infra.db.base import Base
from FlaskApp.domainmodel.account import AccountType


# Module-level function for balance expression
def balance_expr(account_id_col):
    return (
        select(func.coalesce(func.sum(TransactionORM.amount), 0))
        .where(
            TransactionORM.account_id == account_id_col,
            TransactionORM.status.in_(["active", "hidden_active"]),
        )
        .correlate_except(TransactionORM)
        .scalar_subquery()
    )


class AccountORM(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    formatted_account = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    current_balance = column_property(
        select(func.coalesce(func.sum(TransactionORM.amount), 0))
        .where(
            TransactionORM.account_id == id,
            TransactionORM.status.in_(["active", "hidden_active"]),
        )
        .correlate_except(TransactionORM)
        .scalar_subquery()
    )
    available_balance = column_property(
        select(func.coalesce(func.sum(TransactionORM.amount), 0))
        .where(
            TransactionORM.account_id == id,
            TransactionORM.status.in_( ["active", "hidden_active"] ),
            TransactionORM.pending == False
        )
        .correlate_except(TransactionORM)
        .scalar_subquery()
    )
    credit_limit = Column(BigInteger, nullable=True)
    overdrawn = column_property(
        and_(
            func.lower(type).in_([
                AccountType.CHECKING.value,
                AccountType.CREDITCARD.value,
                AccountType.LOAN.value
            ]),
            or_(
                and_(
                    credit_limit.is_not(None),
                    balance_expr(id) < -credit_limit
                ),
                and_(
                    credit_limit.is_(None),
                    balance_expr(id) < 0
                )
            )
        )
    )
    status = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    attributes = relationship("AccountAttributeORM", uselist=True)
    provider_name = Column(String, nullable=False)
    provider_logo = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship(
        "UserORM",
        back_populates="accounts"
    )


class AccountAttributeORM(Base):
    __tablename__ = "account_attributes"

    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), primary_key=True)
    attribute = Column(String, primary_key=True)
