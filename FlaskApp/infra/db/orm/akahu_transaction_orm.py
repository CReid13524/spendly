from sqlalchemy import JSON, UUID, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class AkahuTransactionORM(Base):
    __tablename__ = "akahu_transactions"

    id = Column(String, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    meta = Column(JSON, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=False, unique=True)
    akahu_account_id = Column(String, ForeignKey('akahu_accounts.id'), nullable=False)
    akahu_merchant_id = Column(String, ForeignKey('akahu_merchants.id'), nullable=True)
    akahu_category_id = Column(String, ForeignKey('akahu_categories.id'), nullable=True)

    transaction = relationship("TransactionORM")
    akahu_account = relationship("AkahuAccountORM")
    akahu_merchant = relationship("AkahuMerchantORM")
    akahu_category = relationship("AkahuCategoryORM")
    user = relationship("UserORM")
