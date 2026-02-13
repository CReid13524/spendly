from FlaskApp.domainmodel import Category


def category_domain_to_json(category: Category) -> dict:
    return {
        "id": str(category.id),
        "name": category.name,
        "description": category.description,
        "colour": category.colour,
        "icon": category.icon,
        "type": category.type,
        "parent_category_id": str(category.parent_category.id) if category.parent_category else None,
        "created": category.created.isoformat()
    }