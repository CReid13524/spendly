import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class CategoryORM(Base):
    __tablename__ = 'categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    colour = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    type = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    parent_category = relationship("CategoryORM", remote_side=[id])
    user = relationship("UserORM", back_populates="categories")
