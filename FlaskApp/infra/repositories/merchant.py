from uuid import UUID

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Merchant, User
from FlaskApp.infra.db.mappers import merchant_orm_to_domain, merchant_domain_to_orm, user_orm_to_domain
from FlaskApp.infra.db.orm import MerchantORM


class MerchantRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, merchant: Merchant):
        orm = merchant_domain_to_orm(merchant)
        self.session.add(orm)

    def get(self, merchant_id: str | UUID, user: User) -> Merchant | None:
        if isinstance(merchant_id, str):
            merchant_id = UUID(merchant_id)
        orm = self.session.query(MerchantORM).filter_by(id=merchant_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return merchant_orm_to_domain(orm, user=user)
