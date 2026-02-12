from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Merchant
from FlaskApp.infra.db.mappers import merchant_orm_to_domain, merchant_domain_to_orm
from FlaskApp.infra.db.mappers.user_mapper import user_orm_to_domain
from FlaskApp.infra.db.orm import MerchantORM


class MerchantRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, merchant: Merchant):
        orm = merchant_domain_to_orm(merchant)
        self.session.add(orm)

    def get(self, merchant_id: int) -> Merchant | None:
        orm = self.session.query(MerchantORM).filter_by(id=merchant_id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return merchant_orm_to_domain(orm, user=user)
