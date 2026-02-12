from FlaskApp.domainmodel import Category, User
from FlaskApp.infra.db.orm import CategoryORM


def category_orm_to_domain(
        tx: CategoryORM,
        user: User
) -> Category:
    return Category(
        category_id=tx.id,
        name=tx.name,
        description=tx.description,
        colour=tx.colour,
        icon=tx.icon,
        category_type=tx.type,
        created=tx.created,

        parent_category=category_orm_to_domain(tx.parent_category, user=user) if tx.parent_category else None,
        user=user,
    )


def category_domain_to_orm(
        tx: Category,
) -> CategoryORM:
    return CategoryORM(
        id=tx.id,
        name=tx.name,
        description=tx.description,
        colour=tx.colour,
        icon=tx.icon,
        type=tx.type,
        created=tx.created,
        parent_category_id=tx.parent_category.id if tx.parent_category else None,
        user_id=tx.user.id
    )
