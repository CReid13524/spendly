from FlaskApp.domainmodel import User
from FlaskApp.infra.db.mappers.account_mapper import account_orm_to_domain
from FlaskApp.infra.db.mappers.category_mapper import category_orm_to_domain
from FlaskApp.infra.db.mappers.external_identity_mapper import external_identity_orm_to_domain
from FlaskApp.infra.db.orm import UserORM


def user_orm_to_domain(tx: UserORM) -> User:
    user = User(
        user_id=tx.id,
        email=tx.email,
        name=tx.name,
        password=tx.password,
        status=tx.status,
        created=tx.created,
        last_active=tx.last_active
    )

    for ext_id_orm in tx.external_identities:
        ext_id = external_identity_orm_to_domain(ext_id_orm)
        user.connect_identity(ext_id)
    for account_orm in tx.accounts:
        account = account_orm_to_domain(account_orm, user=user)
        user.add_account(account)
    for category_orm in tx.categories:
        category = category_orm_to_domain(category_orm, user=user)
        user.add_category(category)

    return user


def user_domain_to_orm(user: User) -> UserORM:
    return UserORM(
        id=user.id,
        email=user.email,
        name=user.name,
        password=user.password,
        status=user.status,
        created=user.created,
        last_active=user.last_active
    )
