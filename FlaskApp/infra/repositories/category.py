from uuid import UUID

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

    def get(self, category_id: str | UUID, user: User) -> Category | None:
        if isinstance(category_id, str):
            category_id = UUID(category_id)
        orm = self.session.query(CategoryORM).filter_by(id=category_id, user_id=user.id).first()
        if orm is None:
            return None
        return category_orm_to_domain(orm, user=user)

    def get_by_user(self, user: User) -> list[Category]:
        orms = self.session.query(CategoryORM).filter_by(user_id=user.id).all()
        return [category_orm_to_domain(orm, user=user) for orm in orms]

    def update(self, category: Category, user: User):
        orm = self.session.query(CategoryORM).filter_by(id=category.id, user_id=user.id).first()
        if orm is None:
            raise Exception("Category not found")
        orm.name = category.name
        orm.description = category.description
        orm.colour = category.colour
        orm.icon = category.icon
        orm.type = category.type
        orm.parent_category_id = category.parent_category.id if category.parent_category else None
        self.session.add(orm)

    def exists(self, category_id: str | UUID, user: User) -> bool:
        if isinstance(category_id, str):
            category_id = UUID(category_id)
        return self.session.query(CategoryORM).filter_by(id=category_id, user_id=user.id).first() is not None

    def delete(self, category_id: str | UUID, user: User):
        if isinstance(category_id, str):
            category_id = UUID(category_id)
        orm = self.session.query(CategoryORM).filter_by(id=category_id, user_id=user.id).first()
        if orm is None:
            raise Exception("Category not found")
        self.session.delete(orm)
