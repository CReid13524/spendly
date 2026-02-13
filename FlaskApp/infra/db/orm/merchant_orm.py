import uuid

from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class MerchantORM(Base):
    __tablename__ = "merchants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nzbn = Column(String, nullable=True)
    name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship("UserORM", uselist=False)
