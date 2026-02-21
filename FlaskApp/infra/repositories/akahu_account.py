from datetime import datetime, timezone

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import AkahuAccount, Account, User
from FlaskApp.infra.db.mappers import akahu_account_orm_to_domain, account_orm_to_domain, akahu_account_domain_to_orm, \
    user_orm_to_domain
from FlaskApp.infra.db.orm import AkahuAccountORM, AkahuAccountAttributeORM


class AkahuAccountRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, akahu_account: AkahuAccount):
        orm = akahu_account_domain_to_orm(akahu_account)
        self._session.add(orm)

    def exists(self, akahu_account_id: str) -> bool:
        return self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id).first() is not None

    def get(self, akahu_account_id: str, user: User) -> AkahuAccount | None:
        orm = self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return akahu_account_orm_to_domain(orm, user=user)

    def get_connected_account_by_id(self, akahu_account_id: str, user: User) -> Account | None:
        orm = self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return account_orm_to_domain(orm.account, user=user)

    def add_or_update(self, akahu_account: AkahuAccount, user: User):
        existing = self._session.query(AkahuAccountORM).filter_by(id=akahu_account.id, user_id=user.id).first()
        if existing:
            existing.authorisation = akahu_account.authorisation
            existing.meta = akahu_account.meta
            existing.connection_id = akahu_account.connection_id
            existing.connection_type = akahu_account.connection_type
            existing.refreshed = akahu_account.refreshed
            existing.name = akahu_account.name
            existing.type = akahu_account.type
            existing.formatted_account = akahu_account.formatted_account
            existing.currency = akahu_account.currency
            existing.current_balance = akahu_account.current_balance
            existing.available_balance = akahu_account.available_balance
            existing.status = akahu_account.status
            existing.credit_limit = akahu_account.credit_limit
            existing.overdrawn = akahu_account.overdrawn
            existing.connection_name = akahu_account.connection_name
            existing.connection_logo = akahu_account.connection_logo

            existing_attrs = {a.attribute: a for a in
                              self._session.query(AkahuAccountAttributeORM).filter_by(account_id=akahu_account.id).all()}

            # Delete removed attributes
            for attr_name, attr_obj in existing_attrs.items():
                if attr_name not in akahu_account.attributes:
                    self._session.delete(attr_obj)

            # Add new attributes
            for attr_name in akahu_account.attributes:
                if attr_name not in existing_attrs:
                    new_attr = AkahuAccountAttributeORM(account_id=akahu_account.id, attribute=attr_name)
                    self._session.add(new_attr)
        else:
            orm = akahu_account_domain_to_orm(akahu_account)
            self._session.add(orm)

    def log_refresh_attempt(self, akahu_account_id: str, user: User):
        existing = self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id, user_id=user.id).first()
        if existing:
            existing.refresh_attempt = datetime.now(tz=timezone.utc)

    def list_akahu_accounts(self, user: User) -> list[AkahuAccount]:
        orms = self._session.query(AkahuAccountORM).filter_by(user_id=user.id).all()
        user = user_orm_to_domain(orms[0].user) if orms else user
        return [akahu_account_orm_to_domain(orm, user=user) for orm in orms]
