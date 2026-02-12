import uuid

from FlaskApp.domainmodel import ExternalIdentity
from FlaskApp.infra.db.orm import ExternalIdentityORM


def external_identity_orm_to_domain(tx: ExternalIdentityORM) -> ExternalIdentity:
    return ExternalIdentity(
        provider=tx.provider,
        external_id=tx.external_id,
        email=tx.email,
        name=tx.name,
        meta=tx.meta,
        avatar_url=tx.avatar_url,
        connected_at=tx.connected_at,
    )


def external_identity_domain_to_orm(external_identity: ExternalIdentity, user_id: uuid.UUID) -> ExternalIdentityORM:
    return ExternalIdentityORM(
        provider=external_identity.provider,
        external_id=external_identity.external_id,
        user_id=user_id,
        email=external_identity.email,
        name=external_identity.name,
        avatar_url=external_identity.avatar_url,
        meta=external_identity.meta,
        connected_at=external_identity.connected_at,
    )
