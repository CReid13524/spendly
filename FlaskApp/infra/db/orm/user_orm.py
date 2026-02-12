import uuid

from sqlalchemy import UUID, Column, DateTime, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=True)  # Allow null for users authenticated via external providers
    status = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    last_active = Column(DateTime, nullable=True)

    accounts = relationship("AccountORM", back_populates="user", uselist=True)
    categories = relationship("CategoryORM", back_populates="user", uselist=True)
    external_identities = relationship("ExternalIdentityORM", uselist=True)
