from sqlalchemy.orm import Session

from FlaskApp.domainmodel import AkahuCategory
from FlaskApp.infra.db.mappers import akahu_category_orm_to_domain, akahu_category_domain_to_orm
from FlaskApp.infra.db.orm.akahu_category_orm import AkahuCategoryORM


class AkahuCategoryRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, akahu_category: AkahuCategory):
        orm = akahu_category_domain_to_orm(akahu_category)
        self._session.add(orm)

    def add_or_update(self, akahu_category: AkahuCategory):
        existing = self._session.query(AkahuCategoryORM).filter_by(id=akahu_category.id).first()
        if existing:
            # Update existing fields
            existing.name = akahu_category.name
            existing.groups = akahu_category.groups
        else:
            orm = akahu_category_domain_to_orm(akahu_category)
            self._session.add(orm)

    def get(self, akahu_category_id: str) -> AkahuCategory | None:
        orm = self._session.query(AkahuCategoryORM).filter_by(id=akahu_category_id).first()
        if orm is None:
            return None
        return akahu_category_orm_to_domain(orm)

    def exists(self, akahu_category_id: str) -> bool:
        return self._session.query(AkahuCategoryORM).filter_by(id=akahu_category_id).first() is not None
