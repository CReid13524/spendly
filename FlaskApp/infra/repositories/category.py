from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Category
from FlaskApp.domainmodel.user import User
from FlaskApp.infra.db.mappers import category_domain_to_orm, category_orm_to_domain
from FlaskApp.infra.db.orm.category_orm import CategoryORM


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, category: Category):
        orm = category_domain_to_orm(category)
        self.session.add(orm)

    def get(self, category_id: int) -> Category | None:
        orm = self.session.query(CategoryORM).filter_by(id=category_id).first()
        if orm is None:
            return None
        return category_orm_to_domain(orm)

    def get_by_user(self, user: User) -> list[Category]:
        orms = self.session.query(CategoryORM).filter_by(user_id=user.id).all()
        return [category_orm_to_domain(orm) for orm in orms]
