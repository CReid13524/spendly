from sqlalchemy.orm import Session

from FlaskApp.domainmodel import AkahuMerchant
from FlaskApp.infra.db.mappers import akahu_merchant_orm_to_domain, akahu_merchant_domain_to_orm
from FlaskApp.infra.db.orm.akahu_merchant_orm import AkahuMerchantORM


class AkahuMerchantRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, akahu_merchant: AkahuMerchant):
        orm = akahu_merchant_domain_to_orm(akahu_merchant)
        self._session.add(orm)

    def add_or_update(self, akahu_merchant: AkahuMerchant):
        existing = self._session.query(AkahuMerchantORM).filter_by(id=akahu_merchant.id).first()
        if existing:
            # Update existing fields
            existing.name = akahu_merchant.name
            existing.nzbn = akahu_merchant.nzbn
            existing.website = akahu_merchant.website
            existing.logo = akahu_merchant.logo
        else:
            orm = akahu_merchant_domain_to_orm(akahu_merchant)
            self._session.add(orm)

    def get(self, akahu_merchant_id: str) -> AkahuMerchant | None:
        orm = self._session.query(AkahuMerchantORM).filter_by(id=akahu_merchant_id).first()
        if orm is None:
            return None
        return akahu_merchant_orm_to_domain(orm)

    def exists(self, akahu_merchant_id: str) -> bool:
        return self._session.query(AkahuMerchantORM).filter_by(id=akahu_merchant_id).first() is not None
