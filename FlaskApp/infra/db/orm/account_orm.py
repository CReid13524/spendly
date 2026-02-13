import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Numeric, String, Boolean
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class AccountORM(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    formatted_account = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    current_balance = Column(Numeric, nullable=False)
    available_balance = Column(Numeric, nullable=True)
    credit_limit = Column(Numeric, nullable=True)
    overdrawn = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    attributes = relationship("AccountAttributeORM", uselist=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship(
        "UserORM",
        back_populates="accounts"
    )


class AccountAttributeORM(Base):
    __tablename__ = "account_attributes"

    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), primary_key=True)
    attribute = Column(String, primary_key=True)
