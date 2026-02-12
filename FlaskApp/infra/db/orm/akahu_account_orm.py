from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, UUID
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class AkahuAccountORM(Base):
    __tablename__ = 'akahu_accounts'

    id = Column(String, primary_key=True)
    authorisation = Column(String, nullable=False)
    meta = Column(JSON, nullable=False)
    connection_id = Column(String, nullable=False)
    connection_name = Column(String, nullable=False)
    connection_logo = Column(String, nullable=False)
    connection_type = Column(String, nullable=False)
    refreshed = Column(JSON, nullable=False)
    refresh_attempt = Column(DateTime, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    user = relationship("UserORM")
    account = relationship("AccountORM")
