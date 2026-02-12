from datetime import datetime, timezone

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import AkahuAccount, Account
from FlaskApp.infra.db.mappers import akahu_account_orm_to_domain, account_orm_to_domain, akahu_account_domain_to_orm, \
    user_orm_to_domain
from FlaskApp.infra.db.orm import AkahuAccountORM


class AkahuAccountRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, akahu_account: AkahuAccount):
        orm = akahu_account_domain_to_orm(akahu_account)
        self._session.add(orm)

    def exists(self, akahu_account_id: str) -> bool:
        return self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id).first() is not None

    def get(self, akahu_account_id: str) -> AkahuAccount | None:
        orm = self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return akahu_account_orm_to_domain(orm, user=user)

    def get_connected_account_by_id(self, akahu_account_id: str) -> Account | None:
        orm = self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return account_orm_to_domain(orm.account, user=user)

    def add_or_update(self, akahu_account: AkahuAccount):
        existing = self._session.query(AkahuAccountORM).filter_by(id=akahu_account.id).first()
        if existing:
            # Update existing fields
            existing.authorisation = akahu_account.authorisation
            existing.meta = akahu_account.meta
            existing.connection_id = akahu_account.connection_id
            existing.connection_name = akahu_account.connection_name
            existing.connection_logo = akahu_account.connection_logo
            existing.connection_type = akahu_account.connection_type
            existing.refreshed = akahu_account.refreshed
        else:
            orm = akahu_account_domain_to_orm(akahu_account)
            self._session.add(orm)

    def log_refresh_attempt(self, akahu_account_id: str):
        existing = self._session.query(AkahuAccountORM).filter_by(id=akahu_account_id).first()
        if existing:
            existing.refresh_attempt = datetime.now(tz=timezone.utc)
