import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class UploadORM(Base):
    __tablename__ = "uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    bank = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    status = Column(String, nullable=False)
    upload_transactions = relationship("UploadTransactionORM", backref="upload", cascade="all, delete-orphan",
                                       uselist=True)

    user = relationship("UserORM")


class UploadTransactionORM(Base):
    __tablename__ = "upload_transactions"

    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), primary_key=True)
    upload_id = Column(UUID(as_uuid=True), ForeignKey('uploads.id'), primary_key=True)
