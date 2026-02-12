from sqlalchemy import JSON, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class AkahuCategoryORM(Base):
    __tablename__ = 'akahu_categories'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    groups = Column(JSON, nullable=False)
