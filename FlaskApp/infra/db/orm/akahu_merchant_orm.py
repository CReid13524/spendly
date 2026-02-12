from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from FlaskApp.infra.db.base import Base


class AkahuMerchantORM(Base):
    __tablename__ = "akahu_merchants"

    id = Column(String, primary_key=True)
    nzbn = Column(String, nullable=True)
    name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    logo = Column(String, nullable=True)
