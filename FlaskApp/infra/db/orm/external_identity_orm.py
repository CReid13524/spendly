from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, UUID

from FlaskApp.infra.db.base import Base


class ExternalIdentityORM(Base):
    __tablename__ = 'external_identities'

    provider = Column(String, nullable=False, primary_key=True)
    external_id = Column(String, nullable=False, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    meta = Column(JSON, nullable=False, default={})
    connected_at = Column(DateTime, nullable=False)
