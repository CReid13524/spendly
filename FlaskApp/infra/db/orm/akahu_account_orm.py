from sqlalchemy import JSON, BigInteger, Boolean, Column, DateTime, ForeignKey, String, UUID
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class AkahuAccountORM(Base):
    __tablename__ = 'akahu_accounts'

    # Akahu specific fields
    id = Column(String, primary_key=True)
    authorisation = Column(String, nullable=False)
    meta = Column(JSON, nullable=False)
    connection_id = Column(String, nullable=False)
    connection_type = Column(String, nullable=False)
    refreshed = Column(JSON, nullable=False)
    refresh_attempt = Column(DateTime, nullable=False)

    # Data used by our app - Will be used to create inital AccountORM and then kept up to date for reconciliation
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    formatted_account = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    credit_limit = Column(BigInteger, nullable=True)
    overdrawn = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    attributes = relationship("AkahuAccountAttributeORM", uselist=True)
    current_balance = Column(BigInteger, nullable=False)
    available_balance = Column(BigInteger, nullable=True)
    connection_name = Column(String, nullable=False)
    connection_logo = Column(String, nullable=False)

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    user = relationship("UserORM")
    account = relationship("AccountORM")

class AkahuAccountAttributeORM(Base):
    __tablename__ = 'akahu_account_attributes'

    account_id = Column(String, ForeignKey('akahu_accounts.id'), primary_key=True)
    attribute = Column(String, primary_key=True)