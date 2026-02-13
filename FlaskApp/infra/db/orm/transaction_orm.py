import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Numeric, String, Boolean, Float
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class TransactionORM(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Numeric, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    balance = Column(Numeric, nullable=True)  # Not available via different import methods
    pending = Column(Boolean, nullable=False)
    created = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'), nullable=True)

    user = relationship("UserORM")
    account = relationship("AccountORM")
    category = relationship("CategoryORM")
    merchant = relationship("MerchantORM")
