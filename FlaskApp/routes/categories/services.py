from datetime import datetime, timezone
from uuid import uuid4

from FlaskApp.domainmodel import User, Category
from FlaskApp.infra.unit_of_work import AbstractUnitOfWork


def get_categories(uow: AbstractUnitOfWork, user: User) -> list[Category]:
   with uow:
       categories = uow.categories.get_by_user(user)
       return categories

def create_category(uow: AbstractUnitOfWork, user: User, name: str, description: str, colour: str, icon: str | None, type: str, parent_category_id: str | None):
    # TODO: Category type validation
    with uow:
        parent_category = uow.categories.get(parent_category_id, user=user) if parent_category_id else None
        if parent_category_id and not parent_category:
            raise Exception("Parent category not found")
        category = Category(
            category_id=uuid4(),
            name=name,
            description=description,
            colour=colour,
            icon=icon,
            category_type=type,
            parent_category=parent_category,
            user=user,
            created=datetime.now(tz=timezone.utc)
        )
        uow.categories.add(category)

def update_category(uow: AbstractUnitOfWork, user: User, category_id: str, name: str, description: str, colour: str, icon: str | None, type: str, parent_category_id: str | None):
    # TODO: Category type validation
    parent_category_id = parent_category_id if parent_category_id else None
    parent_category = None
    with uow:
        category = uow.categories.get(category_id, user=user)
        if not category:
            raise Exception("Category not found")
        if parent_category_id:
            parent_category = uow.categories.get(parent_category_id, user=user)
            if not parent_category:
                raise Exception("Parent category not found")
        category.name = name
        category.description = description
        category.colour = colour
        category.icon = icon
        category.type = type
        category.parent_category = parent_category
        uow.categories.update(category, user=user)


def delete_category(uow: AbstractUnitOfWork, user: User, category_id: str):
    with uow:
        if not uow.categories.exists(category_id, user=user):
            raise Exception("Category not found")
        uow.categories.delete(category_id, user=user)
