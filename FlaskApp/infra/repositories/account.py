from uuid import UUID

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Account, User
from FlaskApp.infra.db.mappers import account_orm_to_domain, account_domain_to_orm
from FlaskApp.infra.db.orm import AccountAttributeORM, AccountORM


class AccountRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, account: Account):
        orm = account_domain_to_orm(account)
        self._session.add(orm)

        for attribute in [AccountAttributeORM(account_id=account.id, attribute=attr) for attr in
                          account.attributes]:
            self._session.add(attribute)

    def get(self, account_id: str | UUID, user: User) -> Account | None:
        if isinstance(account_id, str):
            account_id = UUID(account_id)
        orm = self._session.query(AccountORM).filter_by(id=account_id, user_id=user.id).first()
        if orm is None:
            return None
        return account_orm_to_domain(orm, user=user)

    def get_all_for_user(self, user: User) -> list[Account]:
        orms = self._session.query(AccountORM).filter_by(user_id=user.id).all()
        return [account_orm_to_domain(orm, user=user) for orm in orms]

    def exists(self, account_id: str | UUID, user: User) -> bool:
        if isinstance(account_id, str):
            account_id = UUID(account_id)
        return self._session.query(AccountORM).filter_by(id=account_id, user_id=user.id).first() is not None

    def add_or_update(self, account: Account, user: User):
        existing = self._session.query(AccountORM).filter_by(id=account.id, user_id=user.id).first()
        if existing:
            # Update existing fields
            existing.name = account.name
            existing.type = account.type
            existing.currency = account.currency
            existing.credit_limit = account.credit_limit
            existing.status = account.status
            # Sync attributes
            existing_attrs = {a.attribute: a for a in
                              self._session.query(AccountAttributeORM).filter_by(account_id=account.id).all()}

            # Delete removed attributes
            for attr_name, attr_obj in existing_attrs.items():
                if attr_name not in account.attributes:
                    self._session.delete(attr_obj)

            # Add new attributes
            for attr_name in account.attributes:
                if attr_name not in existing_attrs:
                    new_attr = AccountAttributeORM(account_id=account.id, attribute=attr_name)
                    self._session.add(new_attr)
        else:
            orm = account_domain_to_orm(account)
            self._session.add(orm)

            for attribute in [AccountAttributeORM(account_id=account.id, attribute=attr) for attr in
                              account.attributes]:
                self._session.add(attribute)

    def delete(self, user: User, account_id: str | UUID):
        if isinstance(account_id, str):
            account_id = UUID(account_id)
        orm = self._session.query(AccountORM).filter_by(id=account_id, user_id=user.id).first()
        if not orm:
            raise Exception("Account not found")
        orm.status = 'deleted'
