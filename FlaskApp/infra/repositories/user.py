from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import User, ExternalIdentity
from FlaskApp.infra.db.mappers import user_orm_to_domain, user_domain_to_orm, external_identity_domain_to_orm
from FlaskApp.infra.db.orm import UserORM, ExternalIdentityORM


class UserRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    def add(self, user: User):
        orm = user_domain_to_orm(user)
        self.session.add(orm)

    def get(self, user_id: str | uuid.UUID) -> User | None:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        orm = self.session.query(UserORM).filter_by(id=user_id).first()
        if not orm:
            return None
        return user_orm_to_domain(orm)

    def get_by_email(self, email: str) -> User | None:
        orm = self.session.query(UserORM).filter_by(email=email).first()
        if not orm:
            return None
        return user_orm_to_domain(orm)

    def exists(self, user_id: str | uuid.UUID) -> bool:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        return self.session.query(UserORM).filter_by(id=user_id).first() is not None

    def external_id_exists(self, provider: str, provider_id: str) -> bool:
        # Assume provider+provider_id is unique across all users, so we can check if any user has this external identity
        return (
                self.session.query(ExternalIdentityORM)
                .filter_by(provider=provider, provider_id=provider_id)
                .first() is not None
        )

    def get_user_by_external_id(self, provider: str, external_id: str) -> User | None:
        orm = (
            self.session.query(UserORM)
            .join(ExternalIdentityORM, ExternalIdentityORM.user_id == UserORM.id)
            .filter(ExternalIdentityORM.provider == provider,
                    ExternalIdentityORM.external_id == external_id)
            .first()
        )
        if not orm:
            return None
        return user_orm_to_domain(orm)

    def add_external_identity(self, external_identity: ExternalIdentity, user_id: uuid.UUID):
        orm = external_identity_domain_to_orm(external_identity, user_id)
        self.session.add(orm)

    def active(self, user: User):
        orm = self.session.query(UserORM).filter_by(id=user.id).first()
        if orm:
            orm.last_active = datetime.now(tz=timezone.utc)
